# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/rwstlock.c

## Purpose

Implements an alternate reader/writer lock that is interruptible and may be released by a thread other than the acquirer. It lacks priority inheritance and is built from a mutex plus reader/writer condition variables.

## Key Interfaces

- `rwst_enter()` blocks uninterruptibly.
- `rwst_enter_sig()` blocks interruptibly and returns `EINTR` on signal interruption.
- `rwst_tryenter()` attempts acquisition without blocking.
- `rwst_exit()` releases reader or writer state and wakes readers or one writer according to writer-wanted state.
- `rwst_lock_held()` checks reader or writer state.
- `rwst_init()`/`rwst_destroy()` initialize and destroy internal synchronization.
- `rwst_owner()` returns the encoded owner.

## Behavior

- Readers wait while a writer holds the lock, and ordinary readers also wait when a writer is wanted.
- `RW_READER_STARVEWRITER` can bypass writer-wanted state.
- Writers wait while any reader or writer holds the lock.
- Interrupted writer waiters wake readers if no writer remains held or wanted.

## Dependencies

Uses `rwstlock_t` macros from `sys/rwstlock.h`, mutexes, condition variables, panic state, lockstat probes, and `krw_t` modes.

## Notes for Future Work

- This lock intentionally trades away priority inheritance and strict owner release in exchange for interruptibility and cross-thread release.
