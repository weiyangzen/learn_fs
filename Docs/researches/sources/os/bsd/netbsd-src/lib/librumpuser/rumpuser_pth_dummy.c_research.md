# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_pth_dummy.c

## Purpose
Provides a dummy, single-thread-oriented rumpuser threading backend for builds where real threads are unavailable.

## Main Interfaces
Exports the same rumpuser thread, mutex, rwlock, condition-variable, and current-LWP APIs as `rumpuser_pth.c`, but with simplified in-memory counters and no real blocking synchronization.

## Control Flow And State
`rumpuser_thread_create` and `rumpuser_thread_exit` print an error and abort, making real thread use unsupported. `rumpuser_thread_join` is a no-op success path.

Mutexes are heap-allocated structs with a recursion-like integer count and owner pointer. Entry increments the count and stores the global `curlwp`; exit asserts the count is positive and clears ownership at zero.

Rwlocks use one integer: positive means writer, negative means reader count. Writer entry asserts exclusive ownership, reader entry asserts no writer, downgrade changes `1` to `-1`, and tryupgrade succeeds only when the value is exactly `-1`.

Condition variables do not actually wait or wake. Timed wait just calls `nanosleep` for the requested relative interval and returns success. Waiter reporting always returns zero.

Current LWP identity is one global `struct lwp *curlwp`, set and cleared by `rumpuser_curlwpop`.

## Dependencies
Uses libc allocation, assertions, `nanosleep`, and rumpuser headers. It does not depend on pthreads.

## Risks And Notes
This backend is not thread-safe and intentionally aborts on thread creation. It is useful only for configurations that never require concurrent host threads. CV wait semantics are placeholders and cannot model wakeup races or scheduling behavior.
