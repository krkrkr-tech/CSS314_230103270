# Task 15 — Energy

For `P` nodes running for time `T`, approximate energy is
`E_P = P(P_idle+P_active)T` when all nodes are active.  A one-node run of the
same wall-clock duration uses
`E_1=(P_idle+P_active)T`; therefore `E_P/E_1=P`.

If work is fixed instead, runtime is approximately `T_1/S_A(P)` and active
energy may fall, but static energy is paid for every powered node.  Under
Gustafson's identical-time, expanded-work comparison, linear energy growth is
the expected cost of linear capacity growth; energy efficiency depends on
useful work per joule, not speedup alone.
