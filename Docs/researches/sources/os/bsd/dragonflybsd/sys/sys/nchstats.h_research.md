# File Research: sources/os/bsd/dragonflybsd/sys/sys/nchstats.h

Per-CPU namecache statistics structure.

Key responsibilities:
- Defines cache-aligned `struct nchstats`.
- Tracks good hits, negative hits, bad hits, false hits, misses, long path hits/misses, and unused attempts.

Important behavior:
- Intended to be allocated in per-CPU arrays, hence explicit cache alignment.
- Separates useful positive/negative hits from stale/bad/false hits.

Dependencies:
- Consumed by namecache/namei implementation and sysctl/stat reporting paths.

Notable risks:
- Counters are unsigned long and per-CPU; aggregation code must handle CPU-local arrays.
