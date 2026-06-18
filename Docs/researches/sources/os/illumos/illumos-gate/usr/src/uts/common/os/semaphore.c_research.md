# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/semaphore.c

## Purpose

Implements kernel counting semaphores with dispatcher sleep queues, priority-ordered waiters, interruptible waits, cancellation integration, wakeup handling, and sleep-object operations.

## Key Interfaces

- `sema_init()` initializes count and empty sleep queue.
- `sema_destroy()` asserts no waiters.
- `sema_p()` performs uninterruptible acquire, blocking while count is zero.
- `sema_p_sig()` performs interruptible acquire and returns `1` on signal, abort, must-return, or pending cancellation.
- `sema_v()` increments count and wakes the highest-priority waiter if present.
- `sema_tryp()` attempts nonblocking acquire.
- `sema_held()` returns whether count is nonpositive.

## Sleep Queue Behavior

- `SEMA_BLOCK` transitions the current thread to sleep, records the semaphore as wait channel, inserts into `s_slpq` ordered by dispatch priority, and updates LWP voluntary context-switch state.
- `sema_queue()` and `sema_dequeue()` support priority changes.
- `sema_unsleep()` removes a waiter and sets it runnable through sleep-object callbacks.
- `sema_change_pri()` reorders a sleeping waiter when its priority changes.
- `sema_owner()` returns `NULL` because semaphores have no owner.

## Locking

- Semaphore queues are protected by the sleepq hash lock for the semaphore address.
- Wakeups use high-level dispatcher lock paths because the selected sleeping thread is locked while being dequeued.
- Panic mode makes acquire/release/try/held operations no-ops or successful.

## Dependencies

Uses sleep queues, dispatcher locks, class sleep/wakeup hooks, signal and cancellation checks, schedctl cancellation helpers, DTrace scheduler probes, and LWP accounting.

## Notes for Future Work

- `sema_p_sig()` handles the race where `sema_v()` and interruption happen together by passing the semaphore count/wakeup to the next sleeping thread.
