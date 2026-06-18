# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zrlock.c

## Purpose

`zrlock.c` implements the Zero Reference Lock, a synchronization primitive that acts like a reference count with a non-blocking writer lock available only when the reference count is zero.

## Concept

A ZRL permits multiple concurrent references through `zrl_add()`/`zrl_remove()`. A writer-like user can acquire the lock only with `zrl_tryenter()`, and only when the count is zero. There is no blocking writer enter path, so writer priority and writer-waiter state are intentionally absent.

Special refcount values:

- `ZRL_LOCKED == -1`
- `ZRL_DESTROYED == -2`

`ZRL_LOCKED` is treated as zero references for refcount query purposes.

## Functions

`zrl_init()` initializes the mutex, condition variable, refcount, and debug owner fields.

`zrl_destroy()` asserts zero references, destroys synchronization primitives, and marks the lock destroyed.

`zrl_add_impl()` repeatedly attempts to atomically increment the refcount while it is not locked. If locked, it waits on the condition variable until unlocked. Reader acquisition is reentrant because ownership is not exclusive for readers.

`zrl_remove()` atomically decrements the refcount and asserts it remains nonnegative.

`zrl_tryenter()` atomically changes refcount from `0` to `ZRL_LOCKED`. It returns `1` on success and `0` otherwise.

`zrl_exit()` releases the locked state by setting refcount to `0` under the mutex and broadcasting to waiters.

`zrl_refcount()` returns positive references or zero for locked/zero states.

`zrl_is_zero()` returns true for zero or locked states.

`zrl_is_locked()` returns true only for `ZRL_LOCKED`.

Under `ZFS_DEBUG`, `zrl_owner()` returns the debug owner thread, and add/enter/exit maintain owner/caller tracking.

## Synchronization Design

Fast-path reference acquisition uses `atomic_cas_32()` without taking the mutex. Only the locked state causes waiters to take `zr_mtx` and sleep on `zr_cv`.

Unlock uses the mutex and broadcasts after storing zero, ensuring blocked adders wake and retry.

## Key Dependencies

- Uses illumos mutexes, condition variables, atomics, DTrace debug probe, and thread identity.
- The public wrapper macro/function for `zrl_add()` likely passes caller information into `zrl_add_impl()`.

## Notes for Future Readers

- ZRL is suitable when code needs to prevent new references only at moments where existing references are already zero.
- There is no writer wait path; callers that need blocking writer acquisition should use a different primitive.
- Reader reentry is allowed and explicitly useful for reference-state checks across call chains.
