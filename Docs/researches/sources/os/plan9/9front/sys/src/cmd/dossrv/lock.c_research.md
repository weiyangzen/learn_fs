# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/lock.c

## Purpose
Implements the simple `MLock` primitive used by `dossrv`.

## Key Behavior
- `mlock()` asserts the lock is initialized and not already held, then marks it held.
- `unmlock()` asserts the lock is initialized and held, then releases it.
- `canmlock()` tries to acquire without blocking and returns zero if already held.

## Interfaces And Dependencies
- Uses `panic()` for all lock misuse.
- Operates on `MLock` from `iotrack.h`.

## Notes
This is not a blocking kernel-style lock; it is an internal invariant checker and mutual-exclusion marker for the server’s control flow.
