# File Research: sources/os/bsd/netbsd-src/sys/kern/sched_4bsd.c

Read completely: 569 lines.

Implements the NetBSD 4.4BSD-style scheduler policy hooks. It plugs into the machine-independent scheduler framework with priority decay, round-robin tick handling, nice-value updates, fork/exit CPU accounting, and sysctl exposure of scheduler name and round-robin quantum.

Core scheduling model:
- The central metric is `l_estcpu`, a fixed-point estimate of recent CPU usage.
- `sched_schedclock()` increments `l_estcpu` for running `SCHED_OTHER` LWPs by `ESTCPU_ACCUM`, clamps with `ESTCPULIM`, and recalculates priority.
- `sched_pstats_hook()` decays `l_estcpu` once per scheduler statistics interval unless the LWP slept long enough to defer recalculation until wakeup.
- `updatepri()` applies batched decay for LWPs that slept more than one second before becoming runnable.
- `resetpriority()` computes time-sharing priority from `l_estcpu` and process nice value, then calls `lwp_changepri()` when the priority changes.

Decay and priority math:
- The file documents the classic BSD load-dependent decay formula: decay is approximately `(2 * loadavg) / (2 * loadavg + 1)`.
- `decay_cpu()` performs the fixed-point decay and avoids 64-bit arithmetic on non-LP64 when the multiplication is known safe.
- `decay_cpu_batch()` repeatedly applies decay for sleep intervals, with a shortcut that returns zero after sufficiently long sleeps relative to load.
- `ESTCPU_SHIFT`, `ESTCPU_MAX`, and `ESTCPU_ACCUM` bound how much recent CPU use can influence priority; comments explain the split between estimated CPU history and nice levels.

Round-robin and preemption behavior:
- `sched_tick()` runs every `sched_rrticks` hardclock ticks, defaulting to about 100 ms.
- Idle CPUs are asked to reschedule immediately.
- `SCHED_FIFO` threads are not time-sliced.
- `SCHED_RR` threads are forced toward `mi_switch()` by requesting a reschedule at real-time kernel priority.
- Normal threads first set `SPCF_SEENRR`, then `SPCF_SHOULDYIELD`, and finally can be forced into kernel preemption if they remain stuck in kernel code across intervals.
- On SMT or asymmetric systems, non-first-class CPUs push harder to find a better CPU for the LWP.

Process/LWP lifecycle hooks:
- `sched_nice()` updates `p_nice` under `p_lock` and recalculates all LWPs in the process.
- `sched_proc_fork()` records the parent's first LWP `l_estcpu` and current scheduler tick in the child process.
- `sched_proc_exit()` charges excess child CPU history back to the parent after decaying the inherited estimate from fork time.
- `sched_lwp_fork()` copies `l_estcpu` to the new LWP.
- `sched_lwp_collect()` adds a collected LWP's `l_estcpu` back to the current LWP.
- Hooks such as `sched_wakeup()`, `sched_slept()`, `sched_oncpu()`, and `sched_newts()` are present but no-op for this policy.

Sysctl integration:
- `SYSCTL_SETUP(sysctl_sched_4bsd_setup, ...)` creates `kern.sched`.
- Exposes `kern.sched.name` as `4.4BSD`.
- Exposes `kern.sched.rtts`, reporting the round-robin interval in milliseconds through `sysctl_sched_rtts()`.

Risks and notes:
- Priority recalculation assumes caller-side locking: many functions assert `lwp_locked(l, NULL)` or `p_lock` ownership.
- `sched_tick()` relies on careful locking around `spc_lock()` and comments note possible interruption of priority-inheritance trylock paths.
- Parent chargeback in `sched_proc_exit()` only uses the first LWP of each process and has an old `XXX` about init-parent handling.
- The decay model favors interactive/sleeping threads by design; changes to fixed-point constants can alter system-wide scheduling behavior.
