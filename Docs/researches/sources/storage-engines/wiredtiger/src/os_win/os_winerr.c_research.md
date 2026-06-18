<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_winerr.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_winerr.c

## Purpose
Normalizes Windows error reporting into WiredTiger/POSIX-style errors and formatted messages.

## Important APIs, Types, and Functions
`__wt_getlasterror`, `__wt_map_windows_error`, and `__wt_formatmessage`.

## Control Flow
`__wt_getlasterror` returns `GetLastError` but substitutes `ERROR_INVALID_PARAMETER` for `ERROR_SUCCESS`. Mapping scans a fixed table of common Windows errors to errno values and returns `WT_ERROR` otherwise. Formatting grows/uses the session error buffer and calls `FormatMessageA`, with a fallback string if unavailable.

## State and Persistence Behavior
Only the session error buffer may be modified. No persistent state.

## Dependencies and Integration Points
Used by nearly every Windows OS wrapper for consistent error messages and return values.

## Risks and Edge Cases
Unknown Windows errors collapse to `WT_ERROR`, losing specificity. Formatting must tolerate `session == NULL`. Using `__wt_getlasterror` after CRT failures can produce generic errors.

## Test Signals
Mapping-table tests, unknown-error tests, null-session formatting, and post-error message propagation are useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_winerr.c -->
