"""Create Task 24's vector comparison plot from fit_gustafson.py output."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("fit.csv"))
    parser.add_argument("--output", type=Path, default=Path("scaling_comparison.svg"))
    args = parser.parse_args()
    import matplotlib.pyplot as plt
    with args.input.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    x = [int(row["threads"]) for row in rows]
    measured = [float(row["measured_speedup"]) for row in rows]
    gustafson = [float(row["gustafson_speedup"]) for row in rows]
    amdahl = [float(row["amdahl_speedup"]) for row in rows]
    plt.plot(x, x, "--", label="Ideal linear")
    plt.plot(x, gustafson, label="Gustafson fit")
    plt.plot(x, amdahl, label="Amdahl")
    plt.scatter(x, measured, label="Measured", zorder=3)
    plt.xlabel("Threads"); plt.ylabel("Speedup")
    plt.grid(True, alpha=.3); plt.legend(); plt.tight_layout()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(args.output)


if __name__ == "__main__":
    main()
