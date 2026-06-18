# File Research: sources/local-fs/xfsdump/common/lock.c

## Role

This file implements a simple global critical-region lock for xfsdump/xfsrestore.

It wraps the ordered `qlock` abstraction with a single process-wide lock handle.

## Behavior

- `lock_init()` asserts the lock has not already been initialized and allocates a `QLOCK_ORD_CRIT` qlock.
- `lock()` acquires the global critical lock.
- `unlock()` releases it.

## Dependencies

The implementation depends on `qlock_alloc()`, `qlock_lock()`, and `qlock_unlock()`. The ordering ordinal is defined in `qlock.h`.

## Assumptions

The file does not expose a destroy path. The global lock is expected to live for the lifetime of the process.
