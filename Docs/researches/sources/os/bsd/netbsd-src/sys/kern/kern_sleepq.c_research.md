# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_sleepq.c

Read completely: 636 lines.

Implements NetBSD sleep queues used by condition variables, old sleep/wakeup APIs, and synchronization objects. It bridges wait-channel queues, LWP scheduler state, timeouts, interruptible sleeps, and signal-to-error conversion.

Core structures:
- `sleeptab` is the general-purpose hashed sleep table.
- `sleepq_locks[]` provides per-bucket spin mutexes.
- Individual `sleepq_t` queues are `LIST` heads containing sleeping LWPs.

Initialization and queue management:
- `sleeptab_init()` initializes each sleep-table queue and, once globally, the bucket locks.
- `sleepq_init()` initializes a single queue.
- `sleepq_insert()` inserts an LWP, optionally sorted by effective priority for priority-aware synchronization objects.
- `sleepq_reinsert()`, `sleepq_changepri()`, and `sleepq_lendpri()` reposition sleeping LWPs after priority or inherited-priority changes.

Sleep path:
- `sleepq_enter()` locks the current LWP, transfers to the sleep-queue lock if present, and drops kernel-lock recursion count as needed.
- `sleepq_enqueue()` records wait channel, wait message, sync object, sleep queue, interruptibility, sleep start ticks, and changes the current LWP to `LSSLEEP`.
- `sleepq_block()` performs the actual switch with optional timeout callout. It handles early interruption by cancellation, exit/core-dump flags, pending signals, timeout completion, and re-acquisition of dropped kernel locks.
- `sleepq_sigtoerror()` maps a delivered signal to `ERESTART` or `EINTR` depending on `SA_RESTART`.

Wake and removal:
- `sleepq_remove()` removes an LWP from its queue, clears sleep metadata, converts interruptible wakeups to non-interruptible state, and either leaves stopped/suspended LWPs stopped or makes sleeping LWPs runnable.
- `sleepq_wake()` wakes up to `expected` LWPs sleeping on a wait channel.
- `sleepq_unsleep()` removes one LWP from its queue due to out-of-band interruption.
- `sleepq_timeout()` is the timeout callout; it sets `LW_STIMO` and unsleeps the target if still waiting.

Special behavior:
- `sleepq_transfer()` moves an LWP from one sleep queue to another while updating wait channel, wait message, sync object, lock, and interruptibility.
- `sleepq_uncatch()` clears interruptible-sleep flags.
- `sleepq_abort()` supports autoconfiguration or panic-time sleeps by briefly lowering IPL and returning without real blocking.

Concurrency and notes:
- The sleep queue lock is also lent as the LWP lock while the LWP is queued.
- `LW_CATCHINTR` records the caller's intended interruptibility separately from transient `LW_SINTR`.
- Timeout callout halt is deliberately done in the sleeping LWP's context for cache locality and synchronization.
