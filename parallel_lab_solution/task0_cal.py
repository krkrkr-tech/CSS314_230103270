import argparse, os, platform, sys, time, multiprocessing as mp
from harness import emit_verify_tag

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reads", type=int, default=2_000_000)
    ap.add_argument("--student-id", default="230103270")
    args = ap.parse_args()
    start = time.perf_counter_ns()
    for _ in range(max(1, args.reads)):
        time.perf_counter_ns()
    avg = (time.perf_counter_ns() - start) / max(1, args.reads)
    print("CPU:", platform.processor() or platform.machine())
    print("Physical/logical (best effort):", os.cpu_count(), mp.cpu_count())
    print("Python/OS:", sys.version.split()[0], platform.platform())
    print("timer_call_average_ns:", f"{avg:.2f}")
    print(emit_verify_tag("PHASE0", args.student_id, avg, 0.0))

if __name__ == "__main__":
    mp.freeze_support()
    main()
