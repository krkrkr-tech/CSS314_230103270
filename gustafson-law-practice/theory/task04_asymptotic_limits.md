# Task 04 — Asymptotic Efficiency

`E_G(P)=S_G(P)/P=1-alpha+alpha/P`.  Because `alpha/P -> 0`,

`lim(P->infinity) E_G(P)=1-alpha`.

For Amdahl,
`E_A(P)=1/[P*s+(1-s)]`, hence for every `s>0`,
`lim(P->infinity) E_A(P)=0`; its speedup itself tends to `1/s`.
If `s=0`, both models have unit efficiency.  Gustafson therefore has a
non-zero asymptotic efficiency precisely when the observed serial fraction is
strictly below one, subject to the assumption that it remains stable.
