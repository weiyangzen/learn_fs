<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_mtx_cond.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_mtx_cond.c

## Purpose
Provides Windows condition-variable support for WiredTiger using `CRITICAL_SECTION` and native condition variables.

## Important APIs, Types, and Functions
`__wt_cond_alloc`, `__wt_cond_wait_signal`, `__wt_cond_signal`, and `__wt_cond_destroy`.

## Control Flow
Allocation initializes a critical section and condition variable. Wait increments `waiters`, returns on stored signal, enters the critical section, optionally checks `run_func`, converts microseconds to milliseconds with minimum 1ms and overflow cap, waits, handles timeout as unsignalled, decrements waiters, and panics on unexpected failure. Signal uses a full barrier, stores a signal if no waiters exist, or wakes all under the critical section.

## State and Persistence Behavior
Only in-memory synchronization state changes. `waiters == -1` records a pending signal for the next waiter.

## Dependencies and Integration Points
Used by cross-platform background-thread coordination. Mirrors POSIX condition semantics closely while adapting timeout units.

## Risks and Edge Cases
Timeout rounding can lengthen short waits. The fast-path waiter state must remain consistent with atomic operations. Windows errors other than timeout panic.

## Test Signals
Thread wake/timeout tests, stored-signal tests, run-function cancellation, and high-contention stress are important.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_mtx_cond.c -->
