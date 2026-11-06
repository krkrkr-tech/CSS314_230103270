# Task 20 — Graph Processing

BFS has data-dependent frontiers, skewed degree distributions, duplicate
discovery, and remote queue updates.  PageRank repeats sparse matrix-vector
operations whose memory access is indirect and whose convergence may require
more iterations as the graph expands.  These effects cause load imbalance,
cache misses, atomic contention, and global barriers.

Dense linear algebra has regular partitions and predictable communication;
power-law graphs do not.  Thus graph workloads often have `alpha(P)` and
`C(P)` that grow with P, invalidating the constant-fraction assumption even
when the graph itself grows linearly.
