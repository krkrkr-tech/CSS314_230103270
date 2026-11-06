# Task 17 — 3D Stencil

Compute is `Theta(N^3)` and a subdomain boundary is `Theta(N^2)`, so the
surface/volume ratio is `Theta(1/N)`.  If total volume scales as `P`, then
`N=Theta(P^(1/3))` and the ratio becomes `Theta(P^(-1/3))`: larger global
problems improve the ratio.

For fixed per-processor subdomains, however, each rank's local N is constant,
so its communication/compute ratio does not improve.  Network latency and
multiple halo exchanges can still make the effective alpha increase.
