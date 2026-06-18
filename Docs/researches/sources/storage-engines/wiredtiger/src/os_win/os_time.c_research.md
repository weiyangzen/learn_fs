<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_time.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_time.c

## Purpose
Provides Windows epoch time and local broken-down time conversion.

## Important APIs, Types, and Functions
`__wt_epoch_raw` uses `GetSystemTimeAsFileTime`; `__wt_localtime` wraps `localtime_s`.

## Control Flow
Epoch converts Windows 100ns intervals since 1601 to Unix seconds/nanoseconds by subtracting the Unix epoch offset. Localtime returns success for `localtime_s == 0`, otherwise reports the CRT errno.

## State and Persistence Behavior
No state changes. Wall-clock output feeds diagnostics and time utilities.

## Dependencies and Integration Points
Used by portable time APIs and any Windows fallback timing paths.

## Risks and Edge Cases
Wall-clock changes affect results. Arithmetic assumes standard FILETIME epoch conversion constants and signed range adequacy.

## Test Signals
Tests should compare epoch output with system time tolerance and cover localtime error paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_time.c -->
