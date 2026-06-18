# File Research: sources/os/bsd/netbsd-src/sys/kern/sched_m2.c

Read completely: 468 lines.

Implements the NetBSD M2 scheduler policy hooks. Compared with `sched_4bsd.c`, this scheduler is centered on priority-indexed time slices and priority boosting/penalizing rather than an explicit recent-CPU fixed-point estimator.

Core scheduler state:
- `min_ts`, `max_ts`, and `sched_rrticks` hold minimum time-sharing quantum, maximum time-sharing quantum, and real-time round-robin quantum.
- `ts_map[PRI_COUNT]` maps effective priority to time slice length.
- `high_pri[PRI_COUNT]` maps time-sharing priorities to boosted priorities used after sleeps or starvation.
- `PRI_HIGHEST_TS` defines the top time-sharing priority; priorities above it are treated as real-time.

Initialization:
- `sched_rqinit()` requires `hz >= 100`, sets defaults of about 20 ms minimum time slice, 150 ms maximum time slice, and 100 ms round-robin real-time slice, then calls `sched_precalcts()`.
- `sched_precalcts()` fills `ts_map` so lower numerical time-sharing priorities get larger time slices, and fills `high_pri` for boost behavior.
- Initial `lwp0` setup is partly marked `notyet`; current code directly assigns `lwp0.l_sched.timeslice` from `ts_map`.

Priority and time-slice behavior:
- `sched_newts()` sets an LWP's time slice from `ts_map[lwp_eprio(l)]`.
- `sched_nice()` stores the new process nice value and shifts `SCHED_OTHER` LWP priorities by a coarse nice-derived delta.
- `sched_slept()` rewards non-batch sleeping time-sharing threads by increasing their priority, with special handling for negative nice values.
- `sched_wakeup()` boosts threads that slept at least one second using `high_pri`.
- `sched_pstats_hook()` penalizes repeated CPU-bound batch behavior by lowering priority, and can boost runnable threads that have not run for at least a second.
- `sched_oncpu()` loads the per-CPU scheduler tick counter from the LWP's current time slice.

Tick handling:
- `sched_tick()` runs with the current LWP lock held.
- `SCHED_FIFO` threads reset their time quantum and keep running.
- `SCHED_OTHER` threads have priority decreased numerically on quantum expiration, with positive nice values causing larger decreases.
- If the effective priority is no better than the CPU's maximum runnable priority or a target CPU migration exists, the thread is marked `SPCF_SHOULDYIELD` and the CPU is rescheduled.
- Otherwise the same LWP continues with a refreshed time slice.

Lifecycle hooks:
- `sched_proc_fork()` walks child LWPs and recalculates their time slices.
- `sched_proc_exit()`, `sched_lwp_fork()`, `sched_lwp_collect()`, `sched_setrunnable()`, and `sched_schedclock()` are no-op hooks for this policy.

Sysctl integration:
- `SYSCTL_SETUP(sysctl_sched_m2_setup, ...)` creates `kern.sched`.
- Exposes `kern.sched.name` as `M2`.
- Exposes read-only `rtts` and read-write `maxts`/`mints` in milliseconds.
- `sysctl_sched_mints()` and `sysctl_sched_maxts()` validate new values, lock every CPU scheduler state, update the global quantum, recalculate maps, and unlock CPUs.

Risks and notes:
- The file still carries TODOs for fair-share queue implementation and NUMA support.
- Updating `min_ts`/`max_ts` takes all CPU scheduler locks and assumes the lock ordering is safe in the shown loop.
- Several hooks are intentionally empty, so this policy depends more heavily on tick/wakeup/sleep transitions than per-hardclock CPU accounting.
- Nice handling is coarse, based on shifts around `NZERO`, and directly mutates priorities for time-sharing LWPs.
