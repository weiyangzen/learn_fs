<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_mtx_cond.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_mtx_cond.c

## Purpose
Provides POSIX condition-variable allocation, timed/untimed wait, broadcast signal, and destruction for WiredTiger's `WT_CONDVAR`.

## Important APIs, Types, and Functions
`__wt_cond_alloc`, `__wt_cond_wait_signal`, `__wt_cond_signal`, and `__wt_cond_destroy` wrap pthread mutex/condition primitives and maintain `cond->waiters`.

## Control Flow
Allocation initializes a mutex and a condition variable, preferring `CLOCK_MONOTONIC` when configured. Wait increments `waiters`; if the prior value indicates a stored signal, it returns immediately. Otherwise it locks, optionally checks `run_func`, calculates an absolute timeout, waits, treats timeout/EINTR as unsignalled, decrements waiters, unlocks, and panics on unexpected pthread errors. Signal uses a full memory barrier, records a fast-path signal when no waiters exist, or broadcasts under the mutex.

## State and Persistence Behavior
Only in-memory synchronization state changes. `waiters == -1` represents a pending signal for the next waiter, avoiding lost wakeups in common exit paths.

## Dependencies and Integration Points
Used broadly by eviction, checkpoint, logging, and service threads. Integrates with tracking macros, stats, verbose mutex logging, and `__wt_epoch_raw` fallback for timed waits.

## Risks and Edge Cases
Lost wakeup avoidance depends on `waiters` atomic transitions and the optional `run_func`. Timed waits without monotonic pthread support can be affected by wall-clock changes. Destroy panics on live/invalid primitives.

## Test Signals
Threaded wake/wait tests, timeout behavior, stored-signal fast path, run-function cancellation, and sanitizer runs for destroy races are useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_mtx_cond.c -->
