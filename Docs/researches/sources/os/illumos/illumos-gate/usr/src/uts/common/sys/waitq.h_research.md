# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/waitq.h

`waitq.h` declares a kernel-only wait queue abstraction for scheduler threads. The exported `waitq_t` stores a dispatcher lock, first queued thread pointer, queued-thread count, and a blocked flag. The lock protects all fields.

The API initializes and finalizes queues, enqueues a `kthread_t`, wakes a specific queued thread, changes priority for a queued thread, wakes the first queued thread, tests emptiness, and blocks or unblocks future enqueues. `waitq_enqueue()` returns success/failure because enqueue attempts fail when the queue is blocked.

This header depends on kernel thread and dispatcher-lock types. It is a compact synchronization primitive for code that needs explicit control over waiters rather than a plain condition variable.
