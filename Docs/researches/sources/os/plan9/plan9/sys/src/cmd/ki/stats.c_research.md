# File Research: sources/os/plan9/plan9/sys/src/cmd/ki/stats.c

This file provides execution and memory statistics for `ki`.

`isum()` walks all instruction dispatch tables, prints per-instruction counts and percentages, aggregates loads, stores, arithmetic, floating point, branches, syscalls, special-register ops, delay slot use, annulled branch cycles, load/store stalls, and total estimated cycles.

`segsum()` prints segment base/end, resident bytes, and reference counts for Stack, Text, Data, and Bss.

`iprofile()` aggregates instruction profile counters by text symbol ranges, sorts by count, prints cycle percentages with symbol and source location, and clears the profile buffer afterward.
