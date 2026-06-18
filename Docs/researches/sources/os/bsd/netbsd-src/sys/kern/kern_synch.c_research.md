# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_synch.c

Read completely: 1277 lines.

Implements machine-independent synchronization and scheduling support: legacy sleep/wakeup wrappers, kernel pause, yield/preempt, kernel preemption, context switching, runnable-state transitions, reboot suspension, priority-change callbacks, runtime accounting, load average, and periodic process statistics.

Synchronization objects:
- `sleep_syncobj` backs normal sleep queues with sorted sleepq behavior and kernel boost priority.
- `sched_syncobj` represents scheduler-managed blocking/runnable state.
- `kpause_syncobj` is a null sleep-queue object for timed pauses where no wakeup is expected.
- `lbolt` is the once-per-second condition variable broadcast by `sched_pstats()`.

Sleep and wake wrappers:
- `tsleep()` and `mtsleep()` are legacy interfaces that resolve a sleep-table bucket, enter/enqueue on a sleepq, release optional interlocks, block with timeout and optional `PCATCH`, and restore locks as requested.
- `kpause()` blocks the current LWP with optional interruptibility and timeout, using the null sleep queue.
- `wakeup()` wakes all LWPs sleeping on a wait channel unless the system is still cold.

Yield, preemption, and preemption points:
- `yield()` and `preempt()` release kernel locks, move through `mi_switch()`, and reacquire locks; `preempt()` marks involuntary preemption.
- `preempt_needed()` checks the current CPU reschedule request with preemption temporarily disabled.
- `preempt_point()` voluntarily preempts long-running kernel code when needed.
- `kpreempt()` handles requested in-kernel preemption, deferring when preemption is disabled, running in softint context, holding/wanting the big kernel lock, or at an unsuitable IPL. It records event counters and lockstat failure timing.
- `kpreempt_disabled()`, `kpreempt_disable()`, and `kpreempt_enable()` expose explicit preemption state.

Context switching:
- `updatertime()` updates per-LWP runtime from `l_stime`, warning once if the timecounter appears to go backwards.
- `nextlwp()` selects the next runnable LWP from scheduler queues or the idle LWP, updates per-CPU priority/idle flags, and clears reschedule state when no slow softints remain.
- `mi_switch()` is the main MI context-switch path. It handles softint handoff, run queue re-enqueue, migration hints, syscall sleep/wakeup time accounting, DTrace vtime hooks, pmap deactivate/activate, `cpu_switchto()`, `LP_RUNNING` release protocol, lwpctl status, PCU switchpoints, and voluntary/involuntary switch counters.

Runnable and suspend state:
- `setrunnable()` transitions `LSSTOP`, `LSSUSPENDED`, `LSSLEEP`, or `LSIDL` LWPs back toward runnable/onproc state, including unsleeping wait-channel LWPs and selecting a CPU.
- `suspendsched()` marks non-system processes stopped for reboot/suspend, sets `LW_WREBOOT`/`LW_WSUSPEND`, wakes interruptible sleepers, and kicks all CPUs to reach user/kernel boundaries.
- `sched_unsleep()` should not be called for scheduler sync objects and panics.

Priority operations:
- `sched_changepri()` changes base priority for runnable/onproc/other LWPs and may reschedule realtime onproc LWPs.
- `sched_lendpri()` changes inherited/protection-derived auxiliary priority with analogous run queue or reschedule handling.
- `syncobj_noowner()` returns no owner for sync objects without ownership.

Periodic stats:
- Defines `ccpu` and `cexp[]` constants for CPU percentage decay and 1/5/15-minute load averages.
- `sched_pstats()` increments sleep/switch stats, calls scheduler LWP stats hooks, updates LWP and process CPU percentages, computes load averages, enforces `RLIMIT_CPU` by sending `SIGXCPU` or `SIGKILL`, broadcasts `lbolt`, and handles negative-runtime warnings.

Concurrency and notes:
- `mi_switch()` assumes the current LWP lock and per-CPU scheduler lock are held and preemption is disabled.
- Soft interrupt integration is explicit: slow softints can be selected before normal runnable LWPs, and fast softint return avoids normal VM-context accounting.
- Resource-limit enforcement uses `psignal()` after dropping `p_lock` while still under `proc_lock`.
