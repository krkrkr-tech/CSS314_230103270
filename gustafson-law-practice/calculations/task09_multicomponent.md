# Task 09 — Composite Serial Phases

The serial fraction is the non-scaled phases:
`alpha=.02+.06=.08`.  Core flux work is `0.92`.

| P | S = P - .08(P-1) |
|---:|---:|
| 512 | 471.12 |
| 2048 | 1884.76 |

The calculation treats both I/O/broadcast and synchronization as serial with
respect to useful domain work.  If synchronization overlaps computation, its
effective alpha should instead be measured experimentally.
