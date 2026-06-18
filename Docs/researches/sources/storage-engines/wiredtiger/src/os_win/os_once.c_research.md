<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_once.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_once.c

## Purpose
Provides one-time process initialization for Windows builds.

## Important APIs, Types, and Functions
`__wt_once` uses Windows one-time initialization support around a caller routine.

## Control Flow
The implementation stores the routine in static state and uses the Windows init-once callback path to run it once for the process.

## State and Persistence Behavior
State is process-local and static. No persistent data is written.

## Dependencies and Integration Points
Used by portable one-time initialization paths that call `__wt_once` without exposing platform-specific primitives.

## Risks and Edge Cases
Like the POSIX wrapper, a single static once state means later different routines are not independently executed. Callback error propagation is limited by Windows `InitOnce` semantics.

## Test Signals
Multi-threaded calls should execute exactly once and leave initialized state visible to all callers.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_once.c -->
