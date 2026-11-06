# Task 06 — alpha = 0.04

`S=0.04+0.96P`, `E=0.96+0.04/P`.

| P | S(P) | E(P) |
|---:|---:|---:|
| 16 | 15.40 | 0.962500 |
| 64 | 61.48 | 0.960625 |
| 256 | 245.80 | 0.960156 |
| 1024 | 983.08 | 0.960039 |
| 4096 | 3932.20 | 0.960010 |
| 16384 | 15728.68 | 0.960002 |

Efficiency approaches 96%, not zero, because the parallel work scales with
the processor count while the measured serial portion remains fixed.
