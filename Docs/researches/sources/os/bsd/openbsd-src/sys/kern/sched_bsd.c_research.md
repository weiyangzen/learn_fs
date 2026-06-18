# File Research: sources/os/bsd/openbsd-src/sys/kern/sched_bsd.c

Read completely: 768 lines.

Implements the classic BSD scheduler policy pieces used by OpenBSD: round-robin prompting, load average calculation, CPU usage decay, priority recalculation, context switching glue, runnable-state transitions, scheduler clock charging, and CPU performance policy sysctls.

Scheduling timers and load:
- `roundrobin()` advances a clock request by `roundrobin_period`, marks the current CPU's scheduler flags with `SPCF_SEENRR`/`SPCF_SHOULDYIELD`, and calls `need_resched()` if there are runnable peers or a yield is due.
- `update_loadavg()` runs every five seconds, combines non-idle CPU count and per-CPU runqueue lengths, and updates 1/5/15 minute load averages with fixed-point decay constants.
- `scheduler_start()` starts `schedcpu()`, `update_loadavg()`, and the performance-policy timeout when dynamic policy is active.

CPU usage and priorities:
- `schedcpu()` runs every second over `allproc`, increments sleep time for sleeping/stopped threads, decays `p_pctcpu`, stops recalculating priorities for threads that slept the whole second, updates CPU tick deltas, computes new estimated CPU with load-sensitive decay, and requeues runnable threads if their priority bucket changes.
- `decay_aftersleep()` applies additional load-sensitive decay to a thread's estimated CPU usage after a long sleep.
- `setpriority()` computes user priority from base `PUSER`, estimated CPU, nice value weighted by `NICE_WEIGHT`, and `MAXPRI`.
- `schedclock()` charges the current non-idle, non-spinning thread one unit of estimated CPU and recalculates its priority.

Switching:
- `yield()` and `preempt()` place the current thread back on its run queue, account voluntary or involuntary context switches, and call `mi_switch()`.
- `mi_switch()` releases the kernel lock on MP kernels before switching, charges runtime, cancels optional per-thread clock interrupts, clears switch-related scheduler flags, chooses the next process, calls `cpu_switchto()` when needed, restores IPL/scheduler lock state, runs SMR idle handling, restarts optional interval/profiling clock interrupts for the resumed thread, records runtime start time, and reacquires the kernel lock if it was held.
- Tracepoints record off-CPU, on-CPU, and remain-on-CPU events.

Runnable transitions:
- `setrunnable()` moves stopped or sleeping threads to run queues, handles races with `P_INSCHED`, emits tracepoints, uses sleep priority or user priority as appropriate, decays priority after long sleep, and clears `p_slptime`.

Performance policy:
- Global policy state includes `cpu_setperf`, `perflevel`, AC policy, and battery policy. Policies are manual, auto, or high.
- `setperf_auto()` samples per-CPU idle and total CPU state counters, detects load requiring full speed, applies downbeat hysteresis before slowing down, and reschedules itself every 100 ms when dynamic policy is active.
- `sysctl_hwsetperf()` exposes manual performance level setting only when AC policy is manual; otherwise it is read-only.
- `sysctl_hwperfpolicy()` reads or writes policy strings such as `manual`, `auto`, `high`, or an AC/battery pair, rejects unsupported manual battery combinations, immediately raises performance for high policy, and starts the dynamic timeout when needed.
