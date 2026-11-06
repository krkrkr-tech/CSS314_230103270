from __future__ import annotations

import argparse
import csv
import math
import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def work(items: int) -> float:
    value = 0.0
    for i in range(items):
        value += math.sin(i * 0.001) ** 2
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threads", nargs="+", type=int,
                        default=list(range(1, (os.cpu_count() or 1) + 1)))
    parser.add_argument("--items-per-thread", type=int, default=10000)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--output", type=Path, default=Path("results.csv"))
    args = parser.parse_args()
    if args.repetitions < 5 or any(t < 1 for t in args.threads):
        parser.error("use at least five repetitions and positive thread counts")
    rows = []
    for threads in args.threads:
        timings = []
        checksum = None
        for _ in range(args.repetitions):
            start = time.perf_counter()
            with ThreadPoolExecutor(max_workers=threads) as pool:
                values = list(pool.map(work, [args.items_per_thread] * threads))
            elapsed = time.perf_counter() - start
            checksum = sum(values)
            timings.append(elapsed)
        rows.append({"threads": threads, "items_per_thread": args.items_per_thread,
                     "mean_seconds": statistics.mean(timings),
                     "stdev_seconds": statistics.stdev(timings),
                     "checksum": checksum})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0])
        writer.writeheader(); writer.writerows(rows)


if __name__ == "__main__":
    main()
