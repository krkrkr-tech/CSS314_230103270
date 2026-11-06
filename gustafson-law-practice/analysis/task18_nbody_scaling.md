# Task 18 — N-Body

Direct evaluation costs `Theta(N^2)`.  With `N=Theta(P)` and ideal distribution,
each rank still performs `Theta(P)` pair work, while all-pairs exchange and
memory can dominate; the serial/communication fraction therefore tends to
increase unless the machine supplies matching bandwidth.

Barnes–Hut costs `Theta(N log N)`, or `Theta(log P)` work per rank under the
same expansion.  Tree construction, traversal imbalance, and remote tree
data remain overhead, but the algorithm scales substantially better.  Neither
case guarantees constant runtime: that is an empirical claim requiring a
bounded overhead term.
