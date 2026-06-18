# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_clockintr.c

## Purpose
Implements the per-CPU clock interrupt scheduling framework used by hardclock, statclock, itimer, profiling clock, round-robin scheduling, and arbitrary bound clock interrupt callbacks.

## Main Responsibilities
- Initializes each CPU's `clockqueue` and optional hardware `intrclock`.
- Binds/unbinds `struct clockintr` objects to CPUs.
- Maintains a sorted pending queue by nanosecond expiration.
- Dispatches expired clock interrupt callbacks from `clockintr_dispatch()`.
- Rearms or triggers the hardware interrupt clock when the next expiration changes.
- Provides deterministic and randomized clock request advancement.
- Aggregates clock interrupt statistics for `sysctl_clockintr()`.
- Provides DDB display helpers for pending/running/idle clock interrupts.

## Key Entry Points
- `clockintr_cpu_init()`: prepares a CPU clock queue, staggers periodic events, binds primary CPU hardclock.
- `clockintr_trigger()`: starts dispatch when an intrclock exists.
- `clockintr_dispatch()`: runs expired callbacks, handles reschedule requests, records lateness/earliness/spurious stats.
- `clockintr_advance()` and `clockrequest_advance()`: advance periodic events.
- `clockrequest_advance_random()`: advances randomized statclock periods.
- `clockintr_cancel()` / `clockintr_cancel_locked()`: remove pending interrupts and suppress in-flight rescheduling.
- `clockintr_bind()` / `clockintr_unbind()`: attach/detach callbacks from a CPU queue.
- `clockqueue_pend_insert()` / `clockqueue_pend_delete()`: sorted queue operations.
- `nsec_advance()`: advances an expiration past `now`, returning skipped periods.

## Key Data
- `struct clockqueue`: owns mutex, pending queue, all-bound queue, current request, stats, running interrupt, and optional hardware intrclock.
- `struct clockrequest`: passed to callbacks to reschedule themselves.
- `CQ_IGNORE_REQUEST` prevents a running interrupt from being requeued after cancellation/rescheduling races.
- `CQ_NEED_WAKEUP` supports `CL_BARRIER` unbind semantics.

## Concurrency
All queue mutation is protected by `cq_mtx` at `IPL_CLOCK`. Dispatch drops the mutex while invoking callbacks, then reacquires it to process reschedule/cancel state.

## Research Notes
The queue is simple sorted insertion rather than a heap. The design favors small per-CPU event sets and explicit callback rescheduling.
