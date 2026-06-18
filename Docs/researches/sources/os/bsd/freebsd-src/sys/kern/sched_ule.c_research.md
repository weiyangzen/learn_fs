# File Research: sources/os/bsd/freebsd-src/sys/kern/sched_ule.c

## Summary
Implements FreeBSD's ULE scheduler. It provides per-CPU run queues, interactive/timeshare priority computation, SMP CPU selection and load balancing, idle stealing, preemption requests, thread migration, scheduler lifecycle hooks, and the `sched_instance` method table registered as `"ULE"`.

## Main Responsibilities
- Maintains scheduler-private `struct td_sched` state for each thread: last/target CPU, affinity tick, slice, `%cpu` accounting window, sleep/runtime history, and migration flags.
- Maintains per-CPU `struct tdq` queues with spin locks, load counters, transferable counts, current thread, lowest runnable priority, timeshare insertion/dequeue offsets, and idle state.
- Divides runnable priorities into realtime/interactive, batch/timeshare, and idle runqueue ranges and chooses runnable threads in that policy order.
- Computes interactivity and timeshare priorities from voluntary sleep/runtime history, recent CPU usage, and process nice value.
- Handles context-switch bookkeeping for running, sleeping, yielding, preempted, migrating, idle, forking, and exiting threads.
- On SMP, selects CPUs using topology-aware least-loaded searches, cache affinity, interrupt affinity, cpuset constraints, and remote preemption/IPI notification.
- Runs long-term load balancing and short idle-time work stealing across CPU topology groups.

## Key APIs and Hooks
- Scheduler instance methods: `sched_ule_add()`, `sched_ule_choose()`, `sched_ule_rem()`, `sched_ule_sswitch()`, `sched_ule_clock()`, `sched_ule_preempt()`, `sched_ule_wakeup()`, `sched_ule_sleep()`, `sched_ule_fork()`, `sched_ule_exit()`, `sched_ule_bind()`, `sched_ule_unbind()`, `sched_ule_affinity()`, `sched_ule_idletd()`, `sched_ule_throw()`, `sched_ule_ap_entry()`.
- Priority helpers: `sched_priority()`, `sched_thread_priority()`, `sched_interact_score()`, `sched_interact_update()`, `sched_pctcpu_update()`.
- Queue helpers: `tdq_add()`, `tdq_runq_add()`, `tdq_runq_rem()`, `tdq_choose()`, `tdq_load_add()`, `tdq_load_rem()`, `tdq_setlowpri()`.
- SMP helpers: `sched_pickcpu()`, `sched_lowest()`, `sched_highest()`, `sched_balance()`, `sched_balance_pair()`, `tdq_move()`, `tdq_steal()`, `tdq_idled()`, `tdq_trysteal()`, `tdq_notify()`, `sched_setcpu()`.
- Tuning interface under `kern.sched.ule`: `quantum`, `slice`, `interact`, `preempt_thresh`, `static_boost`, `idlespins`, `idlespinthresh`, and SMP balancing/stealing knobs.

## Important Behavior
ULE uses one hardware run queue object per CPU. Runnable threads are counted in `tdq_load`; threads on a run queue and running threads both contribute load, while threads with `TDF_NOLOAD` do not contribute to `tdq_sysload`.

Timeshare priorities are not mapped directly to fixed runqueue slots. The batch/timeshare range is treated as a circular set of queues with insertion and dequeue offsets. `sched_ule_clock()` advances the insertion offset over time so lower-priority batch work eventually receives service, and `tdq_advance_ts_deq_off()` tracks the next non-empty batch queue.

Interactive scoring uses voluntary sleep time versus runtime rather than total CPU wait time. Threads below `sched_interact` enter the interactive priority range; other timeshare threads use a CPU-usage window plus nice-derived offset. Runtime/sleep history is capped and decayed to avoid stale behavior dominating forever.

`sched_pctcpu_update()` maintains a sliding, shifted tick window with decay. It is updated on switch, clock, wakeup, and on-demand `%cpu` queries.

Preemption is usually deferred through AST scheduling or `td_owepreempt`; remote CPUs are notified with IPIs only when priority and idle-state checks say it is worthwhile. The remote notification path uses an ordering fence before checking `tdq_cpu_idle`.

SMP CPU choice prefers the previous CPU when cache affinity is still valid and the CPU is idle enough, binds interrupt threads near the interrupt source, searches last-level-cache groups before global topology, and honors thread cpuset masks. Running threads may set `TDF_PICKCPU` so they pick a new CPU at the next switch.

Idle threads first check local load, then may steal from increasingly broad topology groups before entering the machine-dependent idle path. Idle spinning is bounded and disabled for SMT-style groups where spinning would compete with sibling work.

## State and Synchronization
Thread scheduler state is protected by the thread lock, which is normally the owning CPU queue lock while runnable/running. `thread_lock_block()` / `thread_lock_unblock()` are used during migration and switching to prevent lock-order reversals.

Per-CPU `tdq` state is protected by `tdq_lock`, with selected fields read locklessly through atomics. Pairwise queue moves lock queues by address order. Some idle and notification state deliberately uses lockless reads plus fences for fast wakeup paths.

## Dependencies
Depends on FreeBSD thread/proc, runqueue, cpuset, SMP topology, mutex/spinlock, AST, idle, IPI, KTR, SDT, HWPMC, HWT hook, and sysctl infrastructure.

## Risks
Correctness depends on keeping `tdq_load`, `tdq_transferable`, `tdq_lowpri`, runqueue membership, and `td_lock` transitions synchronized. CPU affinity and cpuset changes can force migration and remote preemption. The timeshare circular queue offsets and SMP stealing paths are subtle starvation/fairness mechanisms, so small changes can alter scheduling latency or load balance.
