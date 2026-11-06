# Task 12 — Communication Penalty

Let serial work be `alpha`, scalable computation be `1-alpha`, and normalized
communication cost be `C(P)`.  A useful extended model is

`S_C(P) = P - alpha(P-1) - C(P)`.

For latency `C(P)=beta log_2(P)` or a mesh/global-exchange penalty
`C(P)=gamma sqrt(P)`, the efficiency is

`E_C(P)=1-alpha+alpha/P-C(P)/P`.

The logarithmic case can retain high efficiency over a wider range; the
square-root case eventually removes efficiency unless communication is
overlapped or beta/gamma decreases.  The constants must be fitted from
parallel measurements rather than assumed universal.
