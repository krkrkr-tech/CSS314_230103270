# Task 14 — Isoefficiency

For a parallel algorithm with work `W`, overhead `T_o`, and `P` processors,
efficiency is `E=W/(W+PT_o)`.  Maintaining a fixed E requires
`W=Theta(PT_o)`, the isoefficiency function.

An ideal Gustafson weak-scaling program assigns `Theta(W/P)` work to each
processor and keeps `T_o=Theta(1)` per processor.  Consequently
`W=Theta(P)` and, for an input dimension N, the required dimension follows
the algorithm's work law (for example `N=Theta(P^(1/3))` for a cubic grid).
If communication makes `T_o` grow, the isoefficiency becomes superlinear and
the ideal Gustafson claim no longer applies.
