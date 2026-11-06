# Task 11 — Sun–Ni Memory-Bounded Speedup

Gustafson assumes a fixed-time run and a workload that can expand with `P`:
`S_G=P-alpha(P-1)`.  Sun–Ni instead constrains the problem by memory capacity:
if `M(P)=P M(1)` and the useful workload is `W(M)`, then a memory-bounded
speedup can be expressed as `S_SN(P)=W(PM)/W(M)` relative to the baseline,
with execution-time and serial/communication terms included in the measured
denominator.

Gustafson overestimates throughput when memory bandwidth, capacity, NUMA
traffic, synchronization, or `alpha(P)` grows with P.  It underestimates when
additional memory enables superlinear cache effects or avoids paging.  Sun–Ni
bridges the laws by making the workload-growth function explicit instead of
assuming linear growth.
