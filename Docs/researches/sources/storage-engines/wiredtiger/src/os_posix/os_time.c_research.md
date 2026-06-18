<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_time.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_time.c

## Purpose
Provides raw epoch time and thread-safe local-time conversion for POSIX builds.

## Important APIs, Types, and Functions
`__wt_epoch_raw` uses `clock_gettime(CLOCK_REALTIME)` when available or `gettimeofday`; `__wt_localtime` wraps `localtime_r`.

## Control Flow
Epoch initializes the output to zero, retries the selected syscall, fills seconds/nanoseconds, and panics on failure. Localtime returns success if `localtime_r` returns non-NULL, otherwise reports errno.

## State and Persistence Behavior
No state is persisted. The returned wall-clock time feeds timestamps, diagnostics, and timeout calculations where monotonic time is unavailable.

## Dependencies and Integration Points
Used by condition variables, logging, statistics, and time utilities. Depends on configure-time availability of `clock_gettime` or `gettimeofday`.

## Risks and Edge Cases
Wall-clock adjustments can affect callers using epoch time for intervals. `__wt_epoch_raw` panics on errors to simplify callers.

## Test Signals
Platform startup tests should validate nonzero epoch values and localtime failure handling through fault injection.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_time.c -->
