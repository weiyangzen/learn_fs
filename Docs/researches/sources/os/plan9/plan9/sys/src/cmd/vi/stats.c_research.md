# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/stats.c

Purpose: Reports simulator execution statistics.

Key behavior:
- `isum` prints per-instruction counts and aggregate cycle/load/store/arithmetic/float/syscall/branch/delay-slot summaries.
- `tlbsum` prints TLB accesses, hits, misses, and hit rate.
- `segsum` prints segment base/end, resident bytes, and reference counts.
- `iprofile` aggregates instruction fetch profile counters by text symbol and prints hot functions with source locations.

Dependencies:
- Uses instruction tables from `run.c`, `special.c`, and `float.c`, segment state, TLB state, symbol lookup, and profile counters.

Notable details:
- `cop1` aggregate count is zeroed so floating-point operations are not counted twice.
