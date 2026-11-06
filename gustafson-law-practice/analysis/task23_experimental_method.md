# Task 23 — Experimental Method

`benchmarks/weak_scale_bench/benchmark.py` performs five or more independent
runs for each thread count, records mean and sample standard deviation, and
writes `benchmarks/results.csv`.  `fit_gustafson.py` converts runtime to
speedup relative to the one-thread baseline and estimates alpha by least
squares for `S=P-alpha(P-1)`.

The measured CSV is intentionally not fabricated: run it on the target
machine, then commit the resulting dataset with the hardware audit.
