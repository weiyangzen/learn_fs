# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_cpu.c

## Summary
Provides shared CPU bookkeeping for MI and rump code, including CPU topology construction, CPU model storage, stable-current-CPU checks, and per-CPU counter aggregation.

## Main Responsibilities
- Initializes `cpu_lock`, attached/running CPU sets, and early fake topology.
- Stores and returns the global CPU model string.
- Determines whether code is in soft interrupt context or whether `curcpu()` is stable.
- Records package/core/SMT/NUMA IDs and relative slow/fast CPU classification.
- Builds circular sibling lists for core, package, and package-first relationships.
- Maintains per-CPU counters and synchronized global `cpu_counts`.

## Important Behavior
`cpu_topology_init()` validates topology uniqueness, falls back to fake topology on bogus duplicate package/core/SMT IDs, marks first SMT/core/package CPUs, and marks first-class CPUs either by fast/slow status or core-first status.

`cpu_count_sync()` sums per-CPU counters at `splvm()`, can poll only once per tick, and has a uniprocessor shortcut before MP is online.

## Dependencies
Uses `struct cpu_info`, scheduler flags, `CPU_INFO_FOREACH`, `kcpuset`, atomic tick polling, IPL control, and scheduler/preemption state.

## Risks
Topology building assumes every CPU has a coherent circular sibling list after fallback or MD-provided data. Counter synchronization is intentionally approximate when polling and is sensitive to `CPU_COUNT_MAX` layout assumptions.
