# File Research: sources/os/bsd/freebsd-src/sys/sys/sched.h

Read completely: 380 lines.

## Purpose
Defines the scheduler KPI, scheduler instance dispatch table, scheduler stats/probes, CPU binding/pinning helpers, and POSIX scheduling user ABI.

## Main Elements
- Kernel side declares general scheduler load/runnable/round-robin interval queries.
- Declares process and thread scheduler hooks for fork, exit, class/nice changes, priority lending, sleep/switch/throw, user priority, wakeup, preemption, run-queue add/remove/choose, CPU affinity, and accounting.
- Provides `sched_userret()` inline fast path and slowpath call for restoring user priority on return to userland.
- Defines temporary CPU pin/unpin inline helpers with interrupt fences.
- Defines `SRQ_*` flags for scheduler add/wakeup circumstances and lock-retention behavior.
- Provides optional `SCHED_STATS` per-CPU sysctl statistic macros and declares scheduler SDT probes.
- Declares DTrace virtual-time hooks when enabled.
- Declares scheduler initialization, AP initialization, timer-accounting query, and L2-neighbor lookup.
- Defines `struct sched_instance`, a full scheduler method table, active scheduler pointer, scheduler selection linker-set entry, `DECLARE_SCHEDULER`, and selection routine.
- Userland/POSIX side defines `SCHED_FIFO`, `SCHED_OTHER`, `SCHED_RR`, `struct sched_param`, and scheduling syscall prototypes.

## Dependencies And Integration
Connects process/thread code to concrete scheduler implementations such as ULE, run queues, DTrace/SDT probes, per-CPU stats, linker sets, priority definitions, and POSIX scheduling syscalls.

## Risk Notes
Scheduler implementations must fill the instance table coherently. Pin/unpin must be balanced, priority lending must be unwound correctly, and userland policy constants are ABI.
