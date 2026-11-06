# Task 19 — Monte Carlo

Independent paths are nearly ideal: each worker owns a random stream and
performs constant local work.  Non-zero alpha comes from seed allocation,
stream validation, final reductions, and output serialization.

With a binary reduction tree, combining P partial sums takes
`Theta(log_2 P)` synchronization rounds.  A simple model is
`S(P)=P-alpha(P-1)-beta log_2(P)`.  Independent counter-based generators,
batched reductions, and deferred output keep beta small; a shared locked PRNG
can make alpha grow sharply.
