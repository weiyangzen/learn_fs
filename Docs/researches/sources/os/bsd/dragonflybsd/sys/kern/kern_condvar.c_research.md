# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_condvar.c

## Summary
Implements DragonFly condition-variable primitives on top of `tsleep`, `lksleep`, and `mtxsleep`.

## Main Responsibilities
- Initializes and destroys `struct cv` spinlock state.
- Provides timed wait helpers for lockmgr locks and mutexes.
- Provides signal/broadcast wakeups.
- Exposes `cv_has_waiters`.

## Important Behavior
Wait paths manually interlock with `tsleep_interlock`, increment `cv_waiters` under `cv_lock`, then sleep with `PINTERLOCKED`. `_cv_signal` checks `cv_waiters`; broadcast zeroes the count and calls `wakeup`, while single signal decrements and calls `wakeup_one`.

## Risks
`cv_waiters` is a lightweight waiter hint rather than a fully audited wait-queue count. Timeouts or interrupted sleeps are not decremented in the wait path, so callers should treat `cv_has_waiters` as advisory.
