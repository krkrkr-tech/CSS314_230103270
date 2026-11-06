# Task 13 — Failure Cases

1. **All-pairs N-body:** expanding `N` linearly with `P` changes work from
   `N^2` to `P^2`.  Pair exchange and memory grow faster than available
   parallelism, so constant runtime is not preserved.
2. **Global-synchronization BFS/PageRank:** a growing frontier causes atomic
   contention, irregular remote accesses, and barriers.  The reduction and
   communication terms increase with graph size and `P`, making `alpha(P)` and
   `C(P)` grow.

Both violate the premise that the parallel portion scales linearly while the
serial/communication time stays bounded.
