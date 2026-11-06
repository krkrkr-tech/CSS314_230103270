"""Export Amdahl/Gustafson curves for arbitrary processor counts."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", type=float, default=0.04)
    parser.add_argument("--max-processors", type=int, default=65536)
    parser.add_argument("--output", type=Path, default=Path("speedup.csv"))
    parser.add_argument("--plot", type=Path)
    args = parser.parse_args()
    if not 0.001 <= args.alpha <= 0.20:
        parser.error("alpha must be between 0.001 and 0.20")
    if not 1 <= args.max_processors <= 65536:
        parser.error("max-processors must be between 1 and 65536")
    processors = [1]
    while processors[-1] < args.max_processors:
        processors.append(min(args.max_processors, processors[-1] * 2))
    rows = []
    for p in processors:
        gustafson = p - args.alpha * (p - 1)
        amdahl = 1 / (args.alpha + (1 - args.alpha) / p)
        rows.append({"processors": p, "alpha": args.alpha,
                     "gustafson_speedup": gustafson,
                     "amdahl_speedup": amdahl,
                     "gustafson_efficiency": gustafson / p})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    if args.plot:
        import matplotlib.pyplot as plt
        x = [r["processors"] for r in rows]
        plt.plot(x, [r["gustafson_speedup"] for r in rows], label="Gustafson")
        plt.plot(x, [r["amdahl_speedup"] for r in rows], label="Amdahl")
        plt.plot(x, x, "--", label="Ideal linear")
        plt.xscale("log", base=2)
        plt.xlabel("Processors"); plt.ylabel("Speedup")
        plt.grid(True, alpha=.3); plt.legend(); plt.tight_layout()
        args.plot.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(args.plot, dpi=200)


if __name__ == "__main__":
    main()
