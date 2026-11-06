# Task 08 — Amdahl versus Gustafson

For `s=alpha=.08`, `P=128`:

`S_A=1/(.08+.92/128)=1/.0871875=11.4695`.

`S_G=128-.08(127)=117.84`.

The absolute difference is `106.3705`; relative to Amdahl this is
`106.3705/11.4695*100 = 927.63%`.  Amdahl keeps the workload fixed, whereas
Gustafson expands parallel work to occupy the fixed run time, so divergence
grows with `P`.
