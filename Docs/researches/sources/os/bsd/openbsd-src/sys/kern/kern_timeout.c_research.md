# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_timeout.c

Read completely: 1053 lines.

Implements OpenBSD's timeout/callout subsystem using hierarchical timing wheels, a softclock interrupt, process-context timeout threads, MP-safe timeout handling, barriers, timeout statistics, and DDB inspection support.

Core state:
- `timeout_mutex` protects global timeout queues and statistics.
- Tick-based timeouts use `timeout_wheel[4 * 256]`; absolute uptime timeouts use `timeout_wheel_kc[4 * 256]`.
- `timeout_new` holds newly added or moved timeouts; `timeout_todo` holds softclock-due work; `timeout_proc` and optional `timeout_proc_mp` hold work requiring process context.
- `timeout_ctx_si`, `timeout_ctx_proc`, and optional `timeout_ctx_proc_mp` track each execution context's todo queue and currently running timeout for barrier synchronization.
- `timeout_kclock[]` caches per-kclock last scan, late threshold, and offset; this file currently handles `KCLOCK_UPTIME` absolute timeouts.

Initialization:
- `timeout_startup()` initializes all circular queues, computes wheel level widths, and stores tick duration as `tick_ts`.
- `timeout_proc_init()` establishes the softclock interrupt, initializes WITNESS lock objects, and defers softclock kthread creation.
- `softclock_create_thread()` creates the process-context softclock thread and, on multiprocessor kernels, an MP-safe softclock thread.

Timeout setup and scheduling:
- `timeout_set()`, `timeout_set_proc()`, and `timeout_set_flags()` initialize timeout callbacks, arguments, clock type, and flags; MP-safe is restricted to process-context timeouts.
- `timeout_add()` schedules tick-based timeouts at `ticks + to_ticks`, handles re-adds by rescheduling only when the new deadline is earlier, records kcov process context, and updates statistics.
- `timeout_add_sec()`, `timeout_add_msec()`, `timeout_add_usec()`, and `timeout_add_nsec()` convert wall durations to ticks with rounding-up semantics and overflow saturation.
- `timeout_abs_ts()` schedules `KCLOCK_UPTIME` absolute deadlines and reschedules earlier deadlines immediately.
- `timeout_del()` removes pending timeouts, clears triggered state, and updates cancellation/deletion stats.
- `timeout_del_barrier()` combines deletion with a completion barrier.

Barrier and execution:
- `timeout_barrier()` waits for an in-flight timeout to finish by injecting a same-context barrier timeout that signals a condition variable after the running callback completes.
- `timeout_run()` removes queue state, marks the timeout triggered, records the running timeout in its context, drops `timeout_mutex`, runs the callback under WITNESS/kcov hooks, then reacquires the mutex and clears `tctx_running`.

Wheel processing:
- `timeout_bucket()` chooses an absolute-time wheel bucket by comparing the deadline with the kclock's `kc_lastscan`.
- `timeout_maskwheel()` hashes seconds and nanoseconds into the requested 8-bit wheel level.
- `timeout_hardclock_update()` runs on the primary CPU each hardclock tick, moves expired tick and kclock buckets to `timeout_todo`, updates kclock cached scan/late values from `nanouptime()`, and schedules the softclock interrupt if work exists.
- `softclock()` drains `timeout_new` and `timeout_todo`, reschedules future entries into the appropriate wheel, runs softclock-context callbacks immediately, and wakes process-context workers when needed.
- `softclock_process_tick_timeout()` and `softclock_process_kclock_timeout()` decide whether a timeout is future, late, process-context, MP-safe process-context, or ready to run in softclock.
- `softclock_thread_run()` loops forever sleeping on its process-context queue and running queued timeout callbacks.
- `softclock_thread()` pins the conservative process-context thread to the primary CPU and runs at softclock IPL; `softclock_thread_mp()` drops the kernel lock and runs MP-safe callbacks.

Adjustment and diagnostics:
- `timeout_adjust_ticks()` moves pending tick-based timeouts forward after monotonic clock advances so elapsed time is not skipped.
- `timeout_sysctl()` snapshots `struct timeoutstat` for `KERN_TIMEOUT_STATS`.
- DDB helpers `db_show_callout()`, `db_show_callout_bucket()`, and `db_show_timeout()` print pending timeouts, remaining time, clock type, wheel location, callback argument, and symbol name.
