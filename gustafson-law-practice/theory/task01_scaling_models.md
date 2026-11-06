# Task 01 — Strong and Weak Scaling

Amdahl's 1967 model fixes the total work `W` and divides it between serial
work `sW` and parallel work `(1-s)W`.  Increasing `P` can reduce only the
parallel portion, so `T_A(P)=sT_1+(1-s)T_1/P`.  The problem dimension and total
work stay constant: `W(P)=W(1)`.  This is fixed-size (strong) scaling.

Gustafson's 1988 model fixes the elapsed parallel time and allows the problem
to grow with `P`.  If the observed serial fraction is `alpha`, then the
parallel portion can represent approximately `(1-alpha)P` units of a
single-processor workload.  Thus `W(P)=Theta(PW(1))` for a constant
per-processor workload, while the serial component need not grow at the same
rate.  This is fixed-time (weak) scaling.

The models answer different engineering questions: Amdahl asks how quickly one
fixed job finishes; Gustafson asks how much larger a job can finish in the
same wall-clock time.  Their different reference frames explain their
apparently conflicting limits.
