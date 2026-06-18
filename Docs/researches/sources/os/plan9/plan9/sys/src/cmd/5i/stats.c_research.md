# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/stats.c

## Scope

Runtime statistics and profiling reports for `5i`.

## Behavior

- `isum()` summarizes instruction counts by operation and broad class.
- `tlbsum()` prints TLB access/hit/miss rates.
- `segsum()` prints segment base/end/resident/reference counts.
- `iprofile()` aggregates per-PC instruction profile buckets into text symbols and prints sorted hot functions.

## Dependencies

Uses `itab`, `tlb`, `memory`, `iprof`, Mach symbol iteration, and source printing.

## Risks And Invariants

- Static `Prof prof[5000]` limits profileable text symbols.
- Division by total count in `iprofile()` assumes at least one profiled count once symbols exist.
- Branch delay-slot counters are carried over from older simulator conventions and are not meaningfully updated by ARM handlers.
