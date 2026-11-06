# Task 03 — Serial-Fraction Invariance Paradox

Amdahl measures `s` on one processor, so synchronization, communication, and
contention that appear only after parallelization are hidden in the baseline.
It then assumes that this fixed serial fraction is applied to an arbitrarily
large fixed job, producing the ceiling `1/s`.

Gustafson measures `alpha=T_serial/T_P` in the actual parallel execution.
For a fixed elapsed time, the equivalent serial workload is
`alpha+(1-alpha)P`; the serial overhead is subtracted only once rather than
being multiplied by the number of processors.  If communication grows with
`P`, alpha is not invariant and the measured model exposes that degradation.
The paradox is therefore a frame-of-reference error, not a contradiction:
the two fractions describe different experiments.
