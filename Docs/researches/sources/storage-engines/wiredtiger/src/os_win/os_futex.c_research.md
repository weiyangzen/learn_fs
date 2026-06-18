<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_futex.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_futex.c

## Purpose
Implements WiredTiger futex-style wait/wake primitives on Windows using `WaitOnAddress` and wake-by-address APIs.

## Important APIs, Types, and Functions
`__wt_futex_wait` and `__wt_futex_wake` operate on `WT_FUTEX_WORD`.

## Control Flow
Wait converts a positive microsecond timeout to at least one millisecond, waits while the address equals the expected value, returns the observed wake value on success, and maps Windows errors to `errno` on failure. Wake atomically exchanges the futex word to the wake value and wakes either one or all waiters.

## State and Persistence Behavior
Only the in-memory futex word changes. The implementation relies on x86 TSO memory ordering for seeing wake writes.

## Dependencies and Integration Points
Used by lower-level synchronization code where POSIX builds may use futex syscalls. Links `Synchronization.Lib`.

## Risks and Edge Cases
Comments explicitly note Windows ARM would require review. Timeout precision is millisecond-granularity. Error handling sets global `errno`.

## Test Signals
Concurrency tests should cover one/all wake, timeout, observed wake values, and stress under high contention.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_futex.c -->
