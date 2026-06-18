# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_condvar.c

## Purpose
Implements FreeBSD kernel condition variables on top of sleep queues, including interruptible waits, timed waits, unlock-on-wait variants, signal, and broadcast.

## Key Elements
- Public initialization/destruction: `cv_init()`, `cv_destroy()`.
- Wait variants: `_cv_wait()`, `_cv_wait_unlock()`, `_cv_wait_sig()`, `_cv_timedwait_sbt()`, `_cv_timedwait_sig_sbt()`.
- Wake variants: `cv_signal()`, `cv_broadcastpri()`.
- Waiter accounting: `cv_waiters`, bounded by `CV_WAITERS_BOUND`.
- KTRACE support for context switch tracing when `KTRACE` is enabled.

## Wait Behavior
Common wait paths:
- Assert valid current thread, condition variable, and lock.
- Emit WITNESS sleep warnings.
- Return immediately when `SCHEDULER_STOPPED()` requires it.
- Lock the sleepqueue for the condition variable.
- Increment approximate waiter count.
- Drop `Giant` around the sleep.
- Add the thread to the sleepqueue as `SLEEPQ_CONDVAR`, optionally `SLEEPQ_INTERRUPTIBLE`.
- Release the caller's lock through its lock class before sleeping.
- Sleep through `sleepq_wait()`, `sleepq_wait_sig()`, `sleepq_timedwait()`, or `sleepq_timedwait_sig()`.
- Reacquire the caller lock unless using `_cv_wait_unlock()`.

Timed waits set an sbintime timeout with `sleepq_set_timeout_sbt()`.

## Signal And Broadcast
`cv_signal()`:
- Fast-returns if `cv_waiters` is zero.
- Locks the sleepqueue and rechecks waiters.
- Handles saturated waiter count by checking `sleepq_lookup()`.
- Decrements waiter count when precise.
- Wakes one thread with `sleepq_signal(..., SLEEPQ_DROP, ...)`.

`cv_broadcastpri()`:
- Fast-returns when no waiters are known.
- Converts legacy priority `-1` to `0`.
- Resets waiter count to zero.
- Wakes all waiters with optional priority.

## Invariants
`cv_destroy()` verifies under `INVARIANTS` that no sleepqueue remains associated with the condition variable. `CV_ASSERT` requires the current thread to be running and the lock/cv pointers to be valid.

## Research Notes
`cv_waiters` is an optimization, not an exact unbounded count. Once it reaches `INT_MAX`, signal falls back to checking the sleepqueue so missed wakeups are avoided despite counter saturation.
