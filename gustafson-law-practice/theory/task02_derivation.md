# Task 02 — Derivation of Gustafson's Law

Normalize the measured parallel run to one second:

1. `s + p = 1`, where `s` is serial time and `p` is parallel time.
2. On `P` processors, the parallel work represents `pP` units of serial
   work, while serial work represents `s` units.
3. The equivalent one-processor runtime is therefore `S(P)=s+pP`.
4. Since `p=1-s`, `S(P)=s+(1-s)P`.
5. Rearranging gives `S(P)=P-s(P-1)`.

Writing the observed serial fraction as `alpha` yields
`S(P)=P-alpha(P-1)`.  The subtraction is the serial work that remains
unscaled; all other work is expanded to fill the fixed-time run.
