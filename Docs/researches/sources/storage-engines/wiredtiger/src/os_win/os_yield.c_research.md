<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_yield.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_yield.c

## Purpose
Provides a Windows thread-yield helper.

## Important APIs, Types, and Functions
`__wt_yield(void)` calls `SwitchToThread`.

## Control Flow
Issues a full memory barrier and yields the remainder of the thread's time slice if another ready thread can run.

## State and Persistence Behavior
No persistent state. The barrier contributes to spin-loop synchronization.

## Dependencies and Integration Points
Used by portable backoff and wait loops.

## Risks and Edge Cases
`SwitchToThread` may return without yielding if no suitable thread is ready; the return is ignored.

## Test Signals
Contention stress and progress tests in synchronization-heavy code are the relevant signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_yield.c -->
