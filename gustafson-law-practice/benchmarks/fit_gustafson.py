"""Fit alpha from weak-scaling runtime data and emit comparison curves."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("results.csv"))
    parser.add_argument("--output", type=Path, default=Path("fit.csv"))
    args = parser.parse_args()
    with args.input.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) < 2:
        parser.error("at least two processor counts are required")
    base = float(rows[0]["mean_seconds"])
    points = [(int(r["threads"]), base / float(r["mean_seconds"])) for r in rows]
    # S_G(P) = P - alpha(P-1); least squares through the fixed intercept at P=1.
    numerator = sum((p - 1) * (p - s) for p, s in points)
    denominator = sum((p - 1) ** 2 for p, _ in points)
    alpha = numerator / denominator if denominator else 0.0
    output = [{"threads": p, "measured_speedup": s,
               "gustafson_speedup": p - alpha * (p - 1),
               "amdahl_speedup": 1 / (alpha + (1-alpha)/p)}
              for p, s in points]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output[0]); writer.writeheader()
        writer.writerows(output)
    print(f"observed_alpha={alpha:.8f}")


if __name__ == "__main__":
    main()
