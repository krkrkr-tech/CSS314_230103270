"""Zero-dependency timing, statistics, and verification helpers."""
from dataclasses import dataclass
import multiprocessing as mp
import statistics
import time
from typing import Callable

@dataclass
class BenchStats:
    min_ms: float
    median_ms: float
    iqr_ms: float
    max_ms: float

def fnv1a_hash(value: str) -> int:
    h = 14695981039346656037
    for byte in value.encode("utf-8"):
        h ^= byte
        h = (h * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return h

def run_benchmark(fn: Callable[[], object], warmup_runs=3, timed_runs=9) -> BenchStats:
    for _ in range(max(0, warmup_runs)):
        fn()
    samples = []
    for _ in range(max(1, timed_runs)):
        start = time.perf_counter_ns()
        fn()
        samples.append((time.perf_counter_ns() - start) / 1e6)
    samples.sort()
    return BenchStats(min(samples), statistics.median(samples),
                      statistics.quantiles(samples, n=4, method="inclusive")[2] -
                      statistics.quantiles(samples, n=4, method="inclusive")[0]
                      if len(samples) > 1 else 0.0, max(samples))

def emit_verify_tag(task_id, student_seed, primary_metric, secondary_metric):
    p_log = mp.cpu_count() or 1
    payload = f"{task_id}|{student_seed}|{p_log}|{primary_metric:.4f}|{secondary_metric:.4f}"
    return f"VERIFY_HASH[{task_id}]: {fnv1a_hash(payload):016X} (P_log={p_log})"

def physical_cores():
    try:
        import os
        return max(1, int(os.environ.get("NUMBER_OF_PROCESSORS", "0")) or (mp.cpu_count() or 1))
    except Exception:
        return mp.cpu_count() or 1
