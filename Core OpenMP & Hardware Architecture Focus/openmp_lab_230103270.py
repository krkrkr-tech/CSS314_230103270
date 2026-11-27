"""Instructor reference solution for the OpenMP Python practical lab."""

import hashlib
import json
import math
import os
import time
from pathlib import Path

os.environ["NUMBA_THREADING_LAYER"] = "omp"

import numba as nb
import numpy as np
from numba import get_num_threads, get_thread_id, njit, prange, set_num_threads


STUDENT_NAME = "Gaziz Kairat"
STUDENT_ID = 230103270

assert isinstance(STUDENT_ID, int) and STUDENT_ID > 0
assert (os.cpu_count() or 1) >= 8, "This lab requires at least 8 logical CPU cores."


@njit(parallel=True)
def _omp_probe():
    acc = 0
    for i in prange(64):
        acc += get_thread_id() + 1
    return acc


_ = _omp_probe()
assert nb.threading_layer() == "omp", f"Expected OpenMP, got {nb.threading_layer()}."
assert nb.config.NUMBA_NUM_THREADS >= 8, "Numba must expose at least 8 worker threads."

rng = np.random.default_rng(STUDENT_ID)
N_T1 = 4_000_000 + (STUDENT_ID % 991) * 1024
BINS_T1 = 48 + (STUDENT_ID % 17)
ITERS_T2 = 35_000_000 + (STUDENT_ID % 503) * 10_000
PAD_STRIDE = 8 + (STUDENT_ID % 5) * 8
ROWS_T3 = 12_000 + (STUDENT_ID % 257) * 16
SKEW_MOD = 37 + (STUDENT_ID % 19)
GRID_H = 384 + (STUDENT_ID % 4) * 32
GRID_W = 512 + (STUDENT_ID % 5) * 32
OMEGA_SOR = np.float64(1.72 + (STUDENT_ID % 11) * 0.015)
THREAD_COUNTS = (1, 2, 4, 8)

data_t1 = rng.integers(0, BINS_T1, size=N_T1, dtype=np.int32)
weights_t1 = rng.uniform(0.25, 2.50, size=N_T1).astype(np.float64)

print(
    f"Backend: {nb.threading_layer()} | Logical cores: {os.cpu_count()} | "
    f"Student: {STUDENT_ID}"
)


@njit(parallel=True)
def buggy_hist_omp(indices, weights, num_bins):
    hist = np.zeros(num_bins, dtype=np.int64)
    w_sums = np.zeros(num_bins, dtype=np.float64)
    for i in prange(indices.shape[0]):
        b = indices[i]
        hist[b] += 1
        w_sums[b] += weights[i]
    return hist, w_sums


@njit
def serial_hist_reference(indices, weights, num_bins):
    hist = np.zeros(num_bins, dtype=np.int64)
    w_sums = np.zeros(num_bins, dtype=np.float64)
    for i in range(indices.shape[0]):
        b = indices[i]
        hist[b] += 1
        w_sums[b] += weights[i]
    return hist, w_sums


@njit(parallel=True)
def safe_hist_omp(indices, weights, num_bins):
    max_threads = get_num_threads()
    hist_private = np.zeros((max_threads, num_bins), dtype=np.int64)
    low_private = np.zeros((max_threads, num_bins), dtype=np.int64)
    high_private = np.zeros((max_threads, num_bins), dtype=np.int64)
    worker_hits = np.zeros(max_threads, dtype=np.int64)
    low_mask = np.int64((1 << 30) - 1)
    exact_weight_scale = np.float64(1 << 54)

    for i in prange(indices.shape[0]):
        tid = get_thread_id()
        b = indices[i]
        hist_private[tid, b] += 1

        scaled_weight = np.int64(weights[i] * exact_weight_scale)
        low_private[tid, b] += scaled_weight & low_mask
        high_private[tid, b] += scaled_weight >> 30
        worker_hits[tid] += 1

    hist = np.zeros(num_bins, dtype=np.int64)
    low_total = np.zeros(num_bins, dtype=np.int64)
    high_total = np.zeros(num_bins, dtype=np.int64)
    for tid in range(max_threads):
        for b in range(num_bins):
            hist[b] += hist_private[tid, b]
            low_total[b] += low_private[tid, b]
            high_total[b] += high_private[tid, b]

    w_sums = np.zeros(num_bins, dtype=np.float64)
    for b in range(num_bins):
        high = high_total[b] + (low_total[b] >> 30)
        low = low_total[b] & low_mask
        w_sums[b] = (
            np.float64(high) * np.float64(2.0**-24)
            + np.float64(low) * np.float64(2.0**-54)
        )
    return hist, w_sums, worker_hits


DIAGNOSIS_T1 = (
    "Each histogram increment is a read-modify-write sequence, so concurrent "
    "workers can overwrite updates and lose counts. The weighted-sum update "
    "has the same race. Floating-point addition is not associative, so changing "
    "the grouping or order of additions can change low bits even when integer "
    "increments are atomic. The safe kernel uses private buffers and a fixed "
    "thread-index reduction; exact integer limbs make weighted totals "
    "independent of the OpenMP thread count."
)


def run_task_1():
    set_num_threads(8)
    reference_hist, reference_sums = serial_hist_reference(
        data_t1, weights_t1, BINS_T1
    )
    lost_counts = []
    max_hist_discrepancy = 0
    max_weight_discrepancy = 0.0
    for _ in range(10):
        hist, sums = buggy_hist_omp(data_t1, weights_t1, BINS_T1)
        lost_counts.append(int(N_T1 - np.sum(hist)))
        max_hist_discrepancy = max(
            max_hist_discrepancy,
            int(np.max(np.abs(hist - reference_hist))),
        )
        max_weight_discrepancy = max(
            max_weight_discrepancy,
            float(np.max(np.abs(sums - reference_sums))),
        )

    safe_results = []
    for threads in THREAD_COUNTS:
        set_num_threads(threads)
        result = safe_hist_omp(data_t1, weights_t1, BINS_T1)
        safe_results.append(result)
    hist_t1, wsums_t1, worker_hits_t1 = safe_results[-1]
    for hist, sums, _ in safe_results[:-1]:
        assert np.array_equal(hist_t1, hist)
        assert np.array_equal(wsums_t1, sums)
    assert int(np.sum(hist_t1)) == N_T1
    assert np.all(worker_hits_t1 > 0), "All 8 OpenMP workers must participate."

    result = {
        "lost_counts_10_runs": lost_counts,
        "max_histogram_bin_discrepancy": max_hist_discrepancy,
        "max_weighted_sum_discrepancy": max_weight_discrepancy,
        "safe_histogram_total": int(np.sum(hist_t1)),
        "safe_weighted_sum_total": float(np.sum(wsums_t1)),
        "safe_worker_hits_at_8_threads": worker_hits_t1.tolist(),
        "safe_outputs_bit_identical_at_1_2_4_8_threads": True,
    }
    print("\nTASK 1 - race and deterministic reduction")
    print(json.dumps(result, indent=2))
    return hist_t1, wsums_t1, result


@njit(parallel=True)
def unpadded_state_omp(iters, seed_val):
    n_threads = get_num_threads()
    state = np.zeros(n_threads, dtype=np.int64)
    for t in prange(n_threads):
        tid = get_thread_id()
        x = np.int64(seed_val + tid * 1315423911)
        for step in range(iters):
            x = (
                x * np.int64(6364136223846793005)
                + np.int64(1442695040888963407)
            ) & np.int64(0x7FFFFFFFFFFFFFFF)
            state[tid] ^= x >> 17
    return state


@njit(parallel=True)
def padded_state_omp(iters, seed_val, pad_stride):
    n_threads = get_num_threads()
    state = np.zeros((n_threads, pad_stride), dtype=np.int64)
    for t in prange(n_threads):
        tid = get_thread_id()
        x = np.int64(seed_val + tid * 1315423911)
        for step in range(iters):
            x = (
                x * np.int64(6364136223846793005)
                + np.int64(1442695040888963407)
            ) & np.int64(0x7FFFFFFFFFFFFFFF)
            state[tid, 0] ^= x >> 17
    return state


DIAGNOSIS_T2 = (
    "In the unpadded array, separate workers repeatedly write different int64 "
    "slots that share a 64-byte cache line. MESI coherence must transfer that "
    "line into each writer's exclusive state and invalidate other cores' "
    "copies, causing cache-line ping-pong despite the absence of a logical "
    "data race. Padding places each active slot on a distinct cache line while "
    "keeping the same recurrence and store frequency. The timing ratio is "
    "hardware- and runtime-dependent, so the recorded measurement is reported "
    "rather than assumed."
)


def run_task_2():
    benchmark = {}
    state_t2 = None
    for threads in THREAD_COUNTS:
        set_num_threads(threads)
        unpadded_state_omp(100_000, STUDENT_ID)
        padded_state_omp(100_000, STUDENT_ID, PAD_STRIDE)

        start = time.perf_counter()
        unpadded = unpadded_state_omp(ITERS_T2, STUDENT_ID)
        unpadded_seconds = time.perf_counter() - start

        start = time.perf_counter()
        padded = padded_state_omp(ITERS_T2, STUDENT_ID, PAD_STRIDE)
        padded_seconds = time.perf_counter() - start

        assert np.array_equal(unpadded, padded[:, 0])
        benchmark[str(threads)] = {
            "unpadded_seconds": unpadded_seconds,
            "padded_seconds": padded_seconds,
            "speedup_padded_vs_unpadded": (
                unpadded_seconds / padded_seconds if padded_seconds else None
            ),
            "active_workers": threads,
        }
        if threads == 8:
            state_t2 = padded[:, 0].copy()

    result = {
        "iterations_per_worker": ITERS_T2,
        "pad_stride_int64": PAD_STRIDE,
        "cache_line_padding_bytes": PAD_STRIDE * np.dtype(np.int64).itemsize,
        "benchmarks_by_thread_count": benchmark,
        "equality_verified_at_all_thread_counts": True,
    }
    print("\nTASK 2 - false sharing benchmark")
    print(json.dumps(result, indent=2))
    return state_t2, result


@njit(parallel=True)
def static_skew_omp(rows, student_id, skew_mod):
    n_threads = get_num_threads()
    out = np.zeros(rows, dtype=np.float64)
    ops = np.zeros((n_threads, PAD_STRIDE), dtype=np.int64)
    worker_hits = np.zeros(n_threads, dtype=np.int64)
    for r in prange(rows):
        tid = get_thread_id()
        work_units = 40 + ((r * 7919 + student_id) % skew_mod) ** 2
        score = 0.0
        for j in range(work_units):
            x = (r * 0.001 + j * 0.0001 + (student_id % 1000) * 0.00001)
            score += math.sin(x) * math.cos(x) + math.sqrt(abs(x) + 1.0)
        out[r] = score
        ops[tid, 0] += work_units
        worker_hits[tid] += 1
    return out, ops[:, 0].copy(), worker_hits


@njit(parallel=True)
def balanced_skew_omp(rows, student_id, skew_mod, interleave_stride):
    n_threads = get_num_threads()
    out = np.zeros(rows, dtype=np.float64)
    ops = np.zeros((n_threads, PAD_STRIDE), dtype=np.int64)
    worker_hits = np.zeros(n_threads, dtype=np.int64)
    for k in prange(rows):
        tid = get_thread_id()
        r = (k * interleave_stride) % rows
        work_units = 40 + ((r * 7919 + student_id) % skew_mod) ** 2
        score = 0.0
        for j in range(work_units):
            x = (r * 0.001 + j * 0.0001 + (student_id % 1000) * 0.00001)
            score += math.sin(x) * math.cos(x) + math.sqrt(abs(x) + 1.0)
        out[r] = score
        ops[tid, 0] += work_units
        worker_hits[tid] += 1
    return out, ops[:, 0].copy(), worker_hits


def load_imbalance_ratio(ops):
    active_ops = np.asarray(ops)[np.asarray(ops) > 0]
    assert active_ops.size == 8, "Expected participation from all 8 OpenMP workers."
    return float(np.max(active_ops) / np.min(active_ops))


def run_task_3():
    stride = 7
    while math.gcd(stride, ROWS_T3) != 1:
        stride += 1

    set_num_threads(8)
    static_skew_omp(ROWS_T3, STUDENT_ID, SKEW_MOD)
    balanced_skew_omp(ROWS_T3, STUDENT_ID, SKEW_MOD, stride)

    start = time.perf_counter()
    out_static, static_ops, static_hits = static_skew_omp(
        ROWS_T3, STUDENT_ID, SKEW_MOD
    )
    static_seconds = time.perf_counter() - start
    start = time.perf_counter()
    out_balanced, balanced_ops, balanced_hits = balanced_skew_omp(
        ROWS_T3, STUDENT_ID, SKEW_MOD, stride
    )
    balanced_seconds = time.perf_counter() - start

    output_difference = float(np.max(np.abs(out_static - out_balanced)))
    static_ratio = load_imbalance_ratio(static_ops)
    balanced_ratio = load_imbalance_ratio(balanced_ops)
    assert output_difference < 1e-11
    assert balanced_ratio < 1.15
    assert np.all(static_hits > 0) and np.all(balanced_hits > 0)

    result = {
        "static_seconds_at_8_threads": static_seconds,
        "balanced_seconds_at_8_threads": balanced_seconds,
        "static_load_imbalance_ratio": static_ratio,
        "balanced_load_imbalance_ratio": balanced_ratio,
        "balanced_interleave_stride": stride,
        "max_output_difference": output_difference,
        "static_operations_per_worker": static_ops.tolist(),
        "balanced_operations_per_worker": balanced_ops.tolist(),
        "all_8_workers_participated": True,
    }
    print("\nTASK 3 - skew and load balancing")
    print(json.dumps(result, indent=2))
    return out_balanced, result


DIAGNOSIS_T3 = (
    "A contiguous prange partition can assign neighboring rows to one worker, "
    "so a concentration of expensive rows near a partition boundary can leave "
    "other workers idle at the barrier. The balanced kernel uses a modular "
    "permutation with a stride coprime to the row count, distributing each "
    "worker's contiguous iteration block across the full workload. It retains "
    "the same per-row arithmetic and writes each result to its original row, "
    "so the numerical output is unchanged. Per-thread operation counters "
    "measure the achieved balance; this deterministic interleaving avoids "
    "requiring a contended shared atomic cursor."
)


@njit(parallel=True)
def sor_red_black_step(grid, omega, per_thread_max, worker_hits):
    n_threads = get_num_threads()
    for tid in range(n_threads):
        per_thread_max[tid, 0] = 0.0

    for color in range(2):
        for r in prange(1, grid.shape[0] - 1):
            tid = get_thread_id()
            worker_hits[tid] += 1
            start_c = 1 + ((r + color + 1) & 1)
            for c in range(start_c, grid.shape[1] - 1, 2):
                old_value = grid[r, c]
                new_value = (1.0 - omega) * old_value + 0.25 * omega * (
                    grid[r - 1, c]
                    + grid[r + 1, c]
                    + grid[r, c - 1]
                    + grid[r, c + 1]
                )
                grid[r, c] = new_value
                delta = abs(new_value - old_value)
                if delta > per_thread_max[tid, 0]:
                    per_thread_max[tid, 0] = delta

    max_delta = 0.0
    for tid in range(n_threads):
        if per_thread_max[tid, 0] > max_delta:
            max_delta = per_thread_max[tid, 0]
    return max_delta


@njit
def solve_pde_omp(grid, omega, sweeps, pad_stride):
    n_threads = get_num_threads()
    per_thread_max = np.zeros((n_threads, pad_stride), dtype=np.float64)
    worker_hits = np.zeros(n_threads, dtype=np.int64)
    max_delta = 0.0
    for _ in range(sweeps):
        max_delta = sor_red_black_step(
            grid, omega, per_thread_max, worker_hits
        )
    return grid, max_delta, worker_hits


def make_initial_grid():
    grid = np.zeros((GRID_H, GRID_W), dtype=np.float64)
    grid[0, :] = 100.0
    grid[-1, :] = -50.0
    y = np.linspace(0.0, np.pi, GRID_H)
    x = np.linspace(0.0, np.pi / 2.0, GRID_H)
    grid[:, 0] = 25.0 * np.sin(y)
    grid[:, -1] = 75.0 * np.cos(x)
    return grid


def run_task_4():
    initial = make_initial_grid()
    benchmark = {}
    grids = {}
    final_deltas = {}
    worker_hits = {}
    reference_grid = None

    for threads in THREAD_COUNTS:
        set_num_threads(threads)
        solve_pde_omp(initial.copy(), OMEGA_SOR, 1, PAD_STRIDE)
        start = time.perf_counter()
        grid, max_delta, hits = solve_pde_omp(
            initial.copy(), OMEGA_SOR, 600, PAD_STRIDE
        )
        elapsed = time.perf_counter() - start
        grids[threads] = grid
        final_deltas[threads] = float(max_delta)
        worker_hits[threads] = hits.tolist()
        if threads == 1:
            reference_grid = grid.copy()
        else:
            difference = float(np.max(np.abs(grid - reference_grid)))
            assert difference < 1e-9, (
                f"Thread count {threads} differs from serial by {difference}."
            )
        benchmark[str(threads)] = {"seconds": elapsed}

    baseline = benchmark["1"]["seconds"]
    for threads in THREAD_COUNTS:
        benchmark[str(threads)]["speedup_vs_1_thread"] = (
            baseline / benchmark[str(threads)]["seconds"]
        )

    grid_t4 = grids[8]
    assert np.all(np.asarray(worker_hits[8]) > 0)
    result = {
        "grid_shape": [GRID_H, GRID_W],
        "omega": float(OMEGA_SOR),
        "red_black_sweeps": 600,
        "benchmarks_by_thread_count": benchmark,
        "final_max_cell_delta_by_thread_count": final_deltas,
        "max_abs_difference_from_1_thread_by_thread_count": {
            str(threads): float(np.max(np.abs(grids[threads] - reference_grid)))
            for threads in THREAD_COUNTS
        },
        "worker_hits_at_8_threads": worker_hits[8],
    }
    print("\nTASK 4 - red-black SOR")
    print(json.dumps(result, indent=2))
    return grid_t4, result


def main():
    for idx, diagnosis in enumerate(
        [DIAGNOSIS_T1, DIAGNOSIS_T2, DIAGNOSIS_T3], start=1
    ):
        assert len(diagnosis.strip()) >= 80, f"Complete DIAGNOSIS_T{idx}."

    hist_t1, wsums_t1, task1_results = run_task_1()
    state_t2, task2_results = run_task_2()
    out_t3, task3_results = run_task_3()
    grid_t4, task4_results = run_task_4()

    set_num_threads(8)
    checksum_blob = (
        f"{STUDENT_ID}|"
        f"{int(np.sum(hist_t1))}|{float(np.sum(wsums_t1)):.4f}|"
        f"{int(np.bitwise_xor.reduce(state_t2))}|"
        f"{float(np.sum(out_t3)):.6f}|"
        f"{float(np.sum(grid_t4)):.6f}"
    )
    lab_digest = hashlib.sha256(checksum_blob.encode()).hexdigest()[:20].upper()
    bundle = {
        "instructor": "Instructor - Sufyan bin Uzayr",
        "student_name": STUDENT_NAME,
        "student_id": STUDENT_ID,
        "omp_layer": nb.threading_layer(),
        "cpu_cores": os.cpu_count(),
        "verification_digest": lab_digest,
    }

    output_dir = Path(__file__).resolve().parent
    (output_dir / "openmp_lab_230103270_output.json").write_text(
        json.dumps(bundle, indent=2) + "\n", encoding="utf-8"
    )
    telemetry = {
        "student_id": STUDENT_ID,
        "student_name": STUDENT_NAME,
        "student_parameters": {
            "N_T1": N_T1,
            "BINS_T1": BINS_T1,
            "ITERS_T2": ITERS_T2,
            "PAD_STRIDE": PAD_STRIDE,
            "ROWS_T3": ROWS_T3,
            "SKEW_MOD": SKEW_MOD,
            "GRID_H": GRID_H,
            "GRID_W": GRID_W,
            "OMEGA_SOR": float(OMEGA_SOR),
        },
        "diagnoses": {
            "DIAGNOSIS_T1": DIAGNOSIS_T1,
            "DIAGNOSIS_T2": DIAGNOSIS_T2,
            "DIAGNOSIS_T3": DIAGNOSIS_T3,
        },
        "task_results": {
            "task_1": task1_results,
            "task_2": task2_results,
            "task_3": task3_results,
            "task_4": task4_results,
        },
        "verification_bundle": bundle,
    }
    (output_dir / "openmp_lab_230103270_telemetry.json").write_text(
        json.dumps(telemetry, indent=2) + "\n", encoding="utf-8"
    )

    print("\n=== OPENMP PYTHON LAB VERIFICATION BUNDLE ===")
    print(json.dumps(bundle, indent=2))
    print(f"\nSaved verification bundle: {output_dir / 'openmp_lab_230103270_output.json'}")
    print(f"Saved full telemetry: {output_dir / 'openmp_lab_230103270_telemetry.json'}")


if __name__ == "__main__":
    main()
