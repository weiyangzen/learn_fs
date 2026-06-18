<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_sleep.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_sleep.c

## Purpose
Implements portable sleep for Windows builds.

## Important APIs, Types, and Functions
`__wt_sleep(uint64_t seconds, uint64_t micro_seconds)` wraps `Sleep`.

## Control Flow
Issues a full memory barrier, rounds sub-millisecond sleeps up to one millisecond, converts seconds and microseconds to milliseconds, and calls `Sleep`.

## State and Persistence Behavior
No persistent state. The barrier supports synchronization expectations around sleeping.

## Dependencies and Integration Points
Used by retry/backoff loops and platform-independent sleeps.

## Risks and Edge Cases
Conversion to `DWORD` can overflow for very large sleeps. Windows scheduler granularity can exceed requested time.

## Test Signals
Backoff tests, short-sleep rounding checks, and overflow boundary review are relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_sleep.c -->
