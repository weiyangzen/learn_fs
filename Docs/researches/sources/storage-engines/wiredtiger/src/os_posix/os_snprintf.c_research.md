<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_snprintf.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_snprintf.c

## Purpose
Wraps POSIX `vsnprintf` while accumulating the formatted length in a caller-supplied counter.

## Important APIs, Types, and Functions
`__wt_vsnprintf_len_incr(char *, size_t, size_t *, const char *, va_list)`.

## Control Flow
Calls `vsnprintf`; on non-negative return, adds that length to `*retsizep` and succeeds. On failure, returns current errno through `__wt_errno`.

## State and Persistence Behavior
Only caller buffers and counters are affected. No persistent state.

## Dependencies and Integration Points
Used by portable formatted-buffer builders that need both truncating writes and total required length accounting.

## Risks and Edge Cases
Behavior follows POSIX `vsnprintf`; callers must manage `va_list` lifetime. Counter growth can overflow if caller does not bound it.

## Test Signals
Tests should cover exact fit, truncation, zero-size buffers, invalid format failure, and cumulative length accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_snprintf.c -->
