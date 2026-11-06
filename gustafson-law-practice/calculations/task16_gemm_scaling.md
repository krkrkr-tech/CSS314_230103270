# Task 16 — GEMM Dimension Growth

GEMM work is `Theta(N^3)`.  To keep parallel time fixed with `P` processors,
`N^3/P=constant`, so `N(P)=N_1 P^(1/3)`.  Memory is `Theta(N^2)=Theta(P^(2/3))`.

| P | N/N1 | memory/M1 |
|---:|---:|---:|
| 1 | 1.000 | 1.000 |
| 8 | 2.000 | 4.000 |
| 64 | 4.000 | 16.000 |
| 512 | 8.000 | 64.000 |

This ignores communication and the extra workspace used by a distributed
matrix multiplication implementation.
