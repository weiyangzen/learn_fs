# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_synch.c

## Purpose

`kern_synch.c` implements DragonFlyBSD's sleep/wakeup machinery, interlocked sleeps with locks, direct LWKT sleeps, timeout handling, runnable-state transitions, process stop waits, per-CPU sleep queues, scheduler accounting callouts, load average collection, and debug wakeup sysctls.

## Scheduler Accounting

- Global state includes `lbolt`, `ncpus`, `safepri`, `tsleep_now_works`, load averages, and tunables such as `kern.pctcpu_decay`.
- `schedcpu()` runs once per second on each CPU, scanning processes for stats and resource-limit checks, and wakes `lbolt` waiters on CPU 0.
- `schedcpu_stats()` increments sleep times, updates user scheduler load, recalculates active/recently sleeping LWPs, and decays older sleeping CPU percentage.
- `schedcpu_resource()` totals per-LWP CPU ticks and enforces CPU limits via `SIGXCPU` or `killproc()`.
- `updatepcpu()` computes one-second CPU percentage samples.
- `loadav()` counts runnable LWPs, rolls per-CPU counts into CPU 0's 1/5/15 minute load averages, and reschedules with jitter.
- `sched_setup()` initializes per-CPU scheduler/load callouts and registers `kcollect` load reporting.

## Sleep Queues And `tsleep`

- Sleep queues are per-CPU hash queues (`struct tslpque`) plus a global hash-to-CPU bitmap used to target wakeup IPIs.
- `sleep_early_gdinit()` installs a dummy queue for very early boot.
- `sched_dyninit()` sizes the global sleep hash from `maxproc`, allocates CPU masks, and initializes CPU 0's real queue.
- `sleep_gdinit()` allocates and initializes each CPU's per-CPU queue array.
- `_tsleep_interlock()` queues the current thread on an ident/domain without descheduling, allowing callers to release higher-level locks before entering `tsleep()` without missing wakeups.
- `tsleep_interlock()` and `tsleep_remove()` expose queue interlock/removal.
- `tsleep()` handles early-boot/panic fallback, interruptible sleep, LWP token interlocks, signal checks, user scheduler release, timeout callout setup/cancel, sleep queue cleanup, and EINTR/ERESTART/EWOULDBLOCK returns.
- `endtsleep()` is the timeout callback and schedules the sleeping thread or makes the LWP runnable while coordinating with `TDF_TIMEOUT_RUNNING`.

## Lock-Integrated And Direct Sleeps

- `ssleep()` atomically interlocks, releases a spinlock, sleeps, and reacquires the spinlock.
- `lksleep()` does the same for `struct lock`.
- `mtxsleep()` does the same for `struct mtx`.
- `zsleep()` does the same for a serializer.
- `lwkt_sleep()` directly deschedules the current LWKT thread and optionally marks it signal-interruptible with `TDF_SINTR`.

## Wakeup And Runnable State

- `_wakeup()` scans the current CPU's queue for matching ident/domain, removes and schedules matching threads, supports wake-one, and sends IPIs to other CPUs selected by the global sleep-queue cpumask.
- Public wakeups include `wakeup()`, `wakeup_one()`, `wakeup_mycpu()`, `wakeup_mycpu_one()`, `wakeup_oncpu()`, `wakeup_oncpu_one()`, `wakeup_domain()`, and `wakeup_domain_one()`.
- `wakeup_start_delayed()` and `wakeup_end_delayed()` coalesce up to two wakeups per CPU while in delayed-wakeup mode.
- `setrunnable()` schedules an LWP sleeping/stopped on its owning CPU, or schedules a direct `lwkt_sleep()` waiter marked `TDF_SINTR`.
- `tstop()` records the current LWP as stopped, notifies the parent when all LWPs stop, sleeps while `STOPLWP()` remains true, and decrements stopped counts on resume.

## Debug Interfaces

`debug.wakeup` and `debug.wakeup_umtx` sysctls let privileged callers issue wakeups for raw idents, useful for diagnostics. KTR points cover tsleep and wakeup entry/exit plus interlock misses.

## Risks And Invariants

The file relies on CPU-local critical sections as the sleep/wakeup interlock. Threads must not migrate while queued. Wakeup uses memory fences before reading remote CPU masks to avoid lost wakeups after caller-side state changes. `tsleep()` must not block except by switching away after the queue and timeout state are consistent, and timeout callout races are resolved by forcing the sleeper to wait for `TDF_TIMEOUT_RUNNING` to clear.
