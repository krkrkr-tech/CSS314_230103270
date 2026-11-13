import argparse, ctypes, multiprocessing as mp
from multiprocessing import shared_memory
from harness import emit_verify_tag, run_benchmark

MASK = 0xFFFFFFFFFFFFFFFF
def fs_worker(name, slot, iters):
    shm = shared_memory.SharedMemory(name=name)
    try:
        arr = (ctypes.c_uint64 * 512).from_buffer(shm.buf)
        acc, mult = arr[slot], 6364136223846793005
        for i in range(iters):
            acc = (acc * mult + (i | 1)) & MASK
        arr[slot] = acc
        del arr
    finally:
        shm.close()

def one_run(p, stride, total):
    shm = shared_memory.SharedMemory(create=True, size=4096)
    try:
        each = max(1, total // p)
        jobs = [mp.Process(target=fs_worker, args=(shm.name, i * stride, each)) for i in range(p)]
        for j in jobs: j.start()
        for j in jobs: j.join()
        if any(j.exitcode for j in jobs): raise RuntimeError("false-sharing worker failed")
    finally:
        shm.close(); shm.unlink()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--total", type=int, default=16_000_000)
    ap.add_argument("--processes", type=int, default=min(mp.cpu_count(), 4))
    ap.add_argument("--warmup", type=int, default=2); ap.add_argument("--runs", type=int, default=7)
    ap.add_argument("--student-id", default="230103270")
    a = ap.parse_args(); p = max(1, a.processes)
    results = {}
    for stride in (1, 2, 4, 8, 16, 32):
        s = run_benchmark(lambda: one_run(p, stride, a.total), a.warmup, a.runs)
        results[stride] = s
        print(f"stride={stride} offset={stride*8}B median_ms={s.median_ms:.3f} iqr_ms={s.iqr_ms:.3f} throughput_Mops={a.total/s.median_ms/1000:.3f}")
    print(emit_verify_tag("PHASE1", a.student_id, results[1].median_ms, results[16].median_ms))

if __name__ == "__main__":
    mp.freeze_support(); main()
