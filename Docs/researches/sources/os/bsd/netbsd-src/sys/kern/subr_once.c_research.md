# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_once.c

## Purpose
Provides the backing implementation for NetBSD one-time initialization/finalization objects used by `RUN_ONCE()`-style kernel code.

## Main Entry Points
- `once_init()` initializes the global mutex and condition variable.
- `_init_once()` runs an initializer function exactly once for the first reference, records its error, and returns the stored error to all callers.
- `_fini_once()` decrements the reference count and runs a finalizer when the last user releases the once object.

## Control Flow And State
All once objects share `oncemtx` and `oncecv`. `_init_once()` waits while the object is `ONCE_RUNNING`, increments `o_refcnt`, and when transitioning from zero references marks the object running, drops the lock, calls the initializer, records `o_error`, marks `ONCE_DONE`, and wakes waiters. Other callers wait for any running transition and then return `o_error`.

`_fini_once()` similarly waits for active initialization/finalization, asserts there is a reference to release, and when the count reaches zero marks running, drops the lock, calls the finalizer, resets status to `ONCE_VIRGIN`, and broadcasts.

## Dependencies
Uses kernel mutexes, condition variables, and `once_t` state from `<sys/once.h>`.

## Risks And Notes
Initializer/finalizer callbacks run without `oncemtx`, avoiding deadlock but requiring callbacks to provide their own synchronization for external state. `KASSERT(o_refcnt != 0)` catches overflow after increment and invalid finalization before initialization. A failed initializer still transitions to `ONCE_DONE`; future callers receive the stored error rather than retrying until `_fini_once()` resets the object.
