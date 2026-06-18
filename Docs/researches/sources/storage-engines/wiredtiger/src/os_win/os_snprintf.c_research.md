<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_snprintf.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_snprintf.c

## Purpose
Provides MSVC-compatible formatted-output length accounting matching POSIX-style callers.

## Important APIs, Types, and Functions
`__wt_vsnprintf_len_incr` uses `_vscprintf` and `_vsnprintf_s`.

## Control Flow
For size zero, it only calculates required length. For nonzero size, it rejects NULL buffer/format, writes with `_TRUNCATE`, adds written length on success, and when truncated adds the required length from `_vscprintf`.

## State and Persistence Behavior
Only caller buffers and counters are affected.

## Dependencies and Integration Points
Used by portable string-formatting helpers that expect consistent count accumulation across POSIX and Windows.

## Risks and Edge Cases
The function returns success on truncation after adding required length, so callers must interpret the aggregate size. Invalid parameter handler avoidance depends on explicit NULL/size checks.

## Test Signals
Tests should cover zero-size sizing, exact fit, truncation, NULL inputs, and cumulative count behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_snprintf.c -->
