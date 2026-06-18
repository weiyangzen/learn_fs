# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpfiber.c

## Summary
Implements the fiber-based rumpuser backend: a cooperative ucontext scheduler plus rumpuser thread, lock, condition-variable, clock, parameter, and LWP glue.

## Key Details
- Maintains runnable and exited thread TAILQs, a `current_thread`, optional scheduler hook, and per-thread `ucontext_t` state.
- Schedules cooperatively with round-robin runnable selection and millisecond wakeup times based on `CLOCK_MONOTONIC`.
- Allocates default stacks with `mmap`; externally supplied stacks are marked with `THREAD_EXTSTACK` and are not unmapped on cleanup.
- Supports joinable fiber threads through `THREAD_MUSTJOIN`, `THREAD_JOINED`, and an internal join-wait queue.
- Provides sleep helpers for relative monotonic, absolute monotonic, and absolute realtime waits.
- Implements `rumpuser_init`, clock operations, environment-backed parameters, console/debug output, exit, signal forwarding, thread create/exit/join, mutexes, rwlocks, condition variables, and `curlwp` operations.
- Mutexes are owner-aware and recursive for the same LWP; condition-variable waits temporarily unschedule the rump kernel and release/reacquire the associated mutex.
- RW lock wakeup policy prefers queued writers over readers.

## Notes
The implementation assumes cooperative execution and effectively one active VCPU; `rumpuser_mutex_enter_nowrap` explicitly relies on no preemption.
