# File Research: sources/os/bsd/freebsd-src/sys/sys/blockcount.h

## Purpose
`blockcount.h` defines kernel inline helpers for a waitable atomic block/reference counter.

## Main Interfaces
- `blockcount_init()` initializes the counter.
- `blockcount_acquire()` increments by `n`, checking overflow under `INVARIANTS`.
- `blockcount_release()` decrements by `n`, uses a release fence, checks underflow, and wakes waiters when the count reaches zero.
- `blockcount_sleep()` and `blockcount_wait()` wrap internal sleep/wakeup machinery.

## Implementation Notes
The counter stores count and waiter state in the private `blockcount_t` layout from `sys/_blockcount.h`. `blockcount_wait()` loops on `EAGAIN`, so callers get a stable wait-for-zero operation.

## Dependencies and Constraints
Kernel-only. Depends on atomic operations, `KASSERT`, `_BLOCKCOUNT_COUNT`, `_BLOCKCOUNT_WAITERS`, and a lock object supplied by the caller for sleep coordination.
