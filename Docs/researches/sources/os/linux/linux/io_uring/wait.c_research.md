# File Research: sources/os/linux/linux/io_uring/wait.c

Completion queue wait implementation for io_uring enter/wait paths.

Key responsibilities:
- Implements `io_cqring_wait()` for waiting until a minimum number of CQEs are available.
- Runs local and normal task_work while waiting.
- Handles CQ overflow flushing and dropped-CQE detection.
- Supports wait timeouts, absolute timers, minimum wait time, custom clock, iowait accounting, signal mask override, and NAPI busy looping.
- Provides wake function that considers CQ readiness and pending work.

Important data flows:
- Wait setup first runs task_work, flushes overflow if needed, checks existing user-visible CQEs, then initializes `io_wait_queue` target tail and timeout state.
- Optional sigmask is installed before waiting and restored on exit.
- The wait loop arms either deferred-taskrun wait counts or an exclusive waitqueue entry, schedules with optional hrtimer, runs task_work after wake, flushes CQ overflow, checks wake conditions, and recomputes remaining wait count.
- Minimum-time wait first sleeps until `min_time`, then may switch to normal timeout behavior while lowering deferred-taskrun wait count to one.

Concurrency and locking:
- CQ head/tail reads use RCU-protected rings because ring resize can replace ring mappings.
- Deferred-taskrun waits use `ctx->cq_wait_nr` and memory barriers to coordinate local work wakeups.
- Normal waits use `ctx->cq_wait` waitqueue and autoremove wake function.

Important invariants:
- Waiting is rejected when deferred taskrun work would be run by a non-submitter.
- Return is forced to success if CQ head and tail differ by function exit, even if a timeout/signal occurred.
- Overflow flushing cannot safely be done from the wake function, so the waiter is woken to flush later.
