# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_membarrier.c

Read completely: 254 lines.

## Purpose
Implements the `membarrier(2)` system call, providing process/global memory barrier operations and expedited IPI-based barriers for user-space synchronization runtimes.

## Main Elements
- Defines supported command mask for query, global, global expedited, private expedited, private sync-core expedited, registration, and registration query commands.
- `membarrier_action_seqcst()` executes a sequentially consistent fence.
- `membarrier_action_seqcst_sync_core()` executes a sequentially consistent fence plus `cpu_sync_core()`.
- `do_membarrier_ipi()` fences locally, rendezvous-calls selected CPUs, then fences again.
- `check_cpu_switched()` tracks CPU switch timestamps so non-expedited global barriers can wait until every CPU has either switched or is idle.
- `kern_membarrier()` validates flags/commands, handles registration bits in `p_flag2`, selects CPU masks through all CPUs or `pmap_active_cpus()`, and returns registered command state.
- `sys_membarrier()` is the syscall wrapper.

## Dependencies And Integration
Uses cpusets, SMP rendezvous, scheduler pinning, process flags, thread/pcpu state, vmspace pmap active CPU tracking, pause-with-signal handling, and architecture `cpu_sync_core()`.

## Risk Notes
Expedited commands require prior registration or return `EPERM`. Private expedited commands rely on pmap active CPU masks and architecture assumptions about syscall return after context switches. The global non-expedited path allocates per-CPU switch timestamp storage and may sleep/retry until all CPUs satisfy the ordering condition.
