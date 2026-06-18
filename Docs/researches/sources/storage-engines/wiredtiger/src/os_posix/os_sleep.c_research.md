<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_sleep.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_sleep.c

## Purpose
Implements a portable sleep helper for POSIX builds.

## Important APIs, Types, and Functions
`__wt_sleep(uint64_t seconds, uint64_t micro_seconds)` converts to `timeval` and calls `select`.

## Control Flow
The function issues a full memory barrier, normalizes microseconds into seconds plus remainder, then sleeps with `select(0, NULL, NULL, NULL, &t)`.

## State and Persistence Behavior
No persistent state. The barrier is part of the synchronization contract for callers that sleep while waiting for state changes.

## Dependencies and Integration Points
Used by retry loops, backoff, tests, and service threads that need subsecond sleeps without exposing platform APIs.

## Risks and Edge Cases
`select` interruptions are ignored, so sleeps may end early. Very large inputs rely on `time_t`/`suseconds_t` conversion ranges.

## Test Signals
Backoff timing tests, EINTR stress, and memory-order-sensitive wake/sleep tests are relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_sleep.c -->
