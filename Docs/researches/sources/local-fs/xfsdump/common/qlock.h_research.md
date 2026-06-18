# File Research: sources/local-fs/xfsdump/common/qlock.h

## Role

This header defines the ordered lock and counting semaphore abstraction.

## Lock Ordering

The lock ordinals are:

- `QLOCK_ORD_CRIT`
- `QLOCK_ORD_WIN`
- `QLOCK_ORD_PI`
- `QLOCK_ORD_MLOG`

The comments state that subsequent lock acquisitions must have lower ordinals than currently held locks, and the implementation checks this through per-thread bitmaps.

## API

Lock API:

- `qlock_alloc()`
- `qlock_lock()`
- `qlock_unlock()`

Semaphore API:

- `qsem_alloc()`
- `qsem_free()`
- `qsemP()`
- `qsemV()`
- `qsemPwouldblock()`
- `qsemPavail()`

Handles are opaque `void *` values.
