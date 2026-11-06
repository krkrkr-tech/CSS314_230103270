# Task 10 — Memory Ceiling

Let one node provide `32 GiB = 32*2^30` bytes and let each grid cell require
`b` bytes.  For `P` nodes, total capacity is `32P GiB`, so

`bN^3 <= 32P*2^30`, and
`N_max(P)=floor((32P*2^30/b)^(1/3))`.

For one 8-byte scalar per cell:

| Nodes | Capacity | N_max |
|---:|---:|---:|
| 64 | 2048 GiB | 6502 |
| 512 | 16384 GiB | 13004 |

The exact integer values depend on whether GiB or decimal GB and how many
arrays/halo cells the solver stores; multiply `b` accordingly.
