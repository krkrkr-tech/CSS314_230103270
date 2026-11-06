# Task 24 — Hardware Audit

Record the following alongside each benchmark result:

```text
OS:
CPU model:
Physical/logical cores:
L1/L2/L3 cache sizes:
Memory capacity and channels:
Python and NumPy versions:
Thread affinity/NUMA policy:
```

The plotting script uses measured means and standard errors; it does not
pretend that this repository can know the runner's cache hierarchy.  Deviations
from theory can result from thermal throttling, frequency scaling, memory
bandwidth saturation, OS scheduling, and NUMA placement.  Run each
configuration five times after a warm-up and report the host audit.
