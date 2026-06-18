# File Research: sources/os/bsd/dragonflybsd/sys/sys/vmmeter.h

## Summary
Virtual memory and system activity statistics structures.

## Main Responsibilities
- Defines `struct vmmeter` counters for switches, traps, syscalls, interrupts, VM faults, paging, forks, execs, VM collisions, forwarded interrupts, TLB shootdowns, and lock/wakeup collisions.
- Defines `struct vmstats` for page-size/count, free/reserved thresholds, paging targets, DMA page accounting, and page queue counts.
- Defines `struct vmtotal` five-second systemwide totals.
- Provides optional `PGINPROF` instrumentation arrays.
- Declares kernel rollup functions.

## Important Behavior
The comments state per-CPU `vmmeter` counters roll up into global statistics, while `vmstats` separates mostly fixed data from frequently changing values for cache behavior.

## Risks
Statistics are partly approximate and moving-target oriented. Consumers should not treat all fields as exact instantaneous truth, especially during per-CPU rollup.
