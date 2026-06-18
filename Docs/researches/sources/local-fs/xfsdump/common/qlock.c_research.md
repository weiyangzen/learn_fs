# File Research: sources/local-fs/xfsdump/common/qlock.c

## Role

This file implements ordered mutex locks and counting semaphores used by xfsdump's multithreaded components.

## Ordered Locks

`qlock_alloc()` creates a pthread mutex associated with an ordinal. A process-wide bitmap ensures each ordinal is allocated only once.

`qlock_lock()` enforces two invariants per thread using a thread-local ordinal bitmap:

- the same lock ordinal is not already held
- no lower ordinal lock is currently held when acquiring this lock

Violations are logged and asserted. This implements deadlock-detection/order enforcement according to the project's ordinal scheme.

`qlock_unlock()` verifies ownership in the thread-local bitmap, clears it, and unlocks the pthread mutex.

## Semaphores

The qsem API wraps POSIX semaphores:

- `qsem_alloc()`
- `qsem_free()`
- `qsemP()`
- `qsemV()`
- `qsemPwouldblock()`
- `qsemPavail()`

These are used by the ring buffer implementation to coordinate ready and active message queues.

## Assumptions

The implementation relies heavily on `assert()` for allocation, pthread, and semaphore success. It does not provide runtime recovery for misuse or failed synchronization primitives.
