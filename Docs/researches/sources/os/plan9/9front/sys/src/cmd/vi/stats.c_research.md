# File Research: sources/os/plan9/9front/sys/src/cmd/vi/stats.c

`stats.c` reports simulator execution statistics. `isum()` aggregates counts from primary, special, and COP1 instruction tables into instruction mix, memory cycles, loads/stores, arithmetic, floating point, special-register moves, syscalls, branches, branch-taken rate, and delay-slot usage.

`tlbsum()` reports the synthetic TLB model’s entries, accesses, hits, misses, and hit rate. `segsum()` reports segment resident bytes and references. `iprofile()` maps per-instruction fetch counters back to text symbols and prints a sorted cycle profile with source locations.

The file is diagnostic/reporting logic for performance studies of simulated MIPS binaries.
