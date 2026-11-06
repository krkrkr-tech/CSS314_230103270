# Task 05 — The nCUBE Example

The nCUBE experiment used a 1,024-processor system and expanded the workload
so that the parallel run remained useful at roughly the same elapsed time.
With a measured serial fraction of `0.004`, Gustafson predicts
`S=1024-.004(1023)=1019.908`, which exceeds 1,000x.

Amdahl applied to the same fraction and a fixed-size job predicts
`1/(.004+.996/1024)=~218.6`, apparently much smaller.  The discrepancy is
not a violation of Amdahl: the experiment did not keep the total problem
fixed.  More processors performed proportionally more parallel work, so the
serial setup was amortized over a larger problem.  The historical result
demonstrates that the choice of scaling question determines the relevant law.
