# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_sema.c

Read completely: 175 lines.

## Purpose
Implements kernel counting semaphores backed by a mutex and condition variable.

## Main Elements
- `sema_init()` zeroes the semaphore, initializes the backing mutex and condition variable, validates a nonnegative initial value, and stores the count.
- `sema_destroy()` asserts no waiters remain, then destroys the mutex and condition variable.
- `_sema_post()` increments the count and signals one waiter when waiters exist and the count is positive.
- `_sema_wait()` sleeps in a loop while the count is zero, tracks waiter count around `cv_wait()`, then decrements the count.
- `_sema_timedwait()` waits with a timeout, treats the timeout as a lower bound in the presence of spurious wakeups, and consumes a count on success.
- `_sema_trywait()` consumes a count only if immediately available.
- `sema_value()` returns the current count under the semaphore mutex.
- All operations emit KTR lock tracing with file/line data for wrapped internal calls.

## Dependencies And Integration
Uses kernel mutexes, condition variables, KTR lock tracing, and the public `sys/sema.h` API wrappers.

## Risk Notes
Semaphores do not model a single owner, so priority propagation generally cannot raise a useful owner priority. Destroying with waiters is invalid, and consumers must balance posts and waits to avoid leaked capacity or permanent sleepers.
