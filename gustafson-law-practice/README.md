# Gustafson's Law Practice

Solutions to Tasks 01–25 in *Gustafson Law Practice Tasks*.  The derivations use
the serial fraction measured during the parallel run (`alpha`) unless a task
explicitly calls for Amdahl's fixed-size fraction (`s`).

## Contents

- `theory/`: Tasks 01–05 and 11–15
- `calculations/`: Tasks 06–10, 16–17
- `analysis/`: Tasks 18–20 and 24
- `benchmarks/`: Tasks 21–23

## Core equations

With normalized parallel runtime `T_P = s + p = 1`, `alpha = s`, and
`p = 1 - alpha`:

`S_G(P) = P - alpha(P - 1) = alpha + (1 - alpha)P`

`E_G(P) = S_G(P)/P = 1 - alpha + alpha/P`

For a fixed-size workload with serial fraction `s`:

`S_A(P) = 1 / (s + (1-s)/P)`.

## Running the empirical tools

```text
python benchmarks/simulator.py --alpha 0.04 --output benchmarks/speedup.csv --plot benchmarks/speedup.png
python benchmarks/weak_scale_bench/benchmark.py --threads 1 2 4 --repetitions 5 --output benchmarks/results.csv
python benchmarks/fit_gustafson.py --input benchmarks/results.csv --output benchmarks/fit.csv
```

The benchmark is intentionally configurable because measured thread counts and
hardware vary by host.  Task 24 documents the machine audit needed when results
are collected.
