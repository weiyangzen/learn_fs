<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_utf8.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_utf8.c

## Purpose
Converts between WiredTiger's UTF-8 paths/strings and Windows UTF-16 strings.

## Important APIs, Types, and Functions
`__wti_to_utf16_string` wraps `MultiByteToWideChar`; `__wti_to_utf8_string` wraps `WideCharToMultiByte`.

## Control Flow
Each function first queries required buffer size, allocates a scratch buffer, performs conversion including the terminating NUL, sets `WT_ITEM.size`, and frees the scratch buffer on conversion failure.

## State and Persistence Behavior
No persistent state. Returned scratch buffers are session-owned temporaries freed by callers with `__wt_scr_free`.

## Dependencies and Integration Points
Used throughout Windows filesystem and directory code before calling wide-character Win32 APIs.

## Risks and Edge Cases
The error check expects `ERROR_INSUFFICIENT_BUFFER` patterns that sizing calls may not actually set; malformed UTF-8/wide strings must be tested. `WT_ITEM.size` is a count returned by Windows, not necessarily byte semantics for UTF-16 callers.

## Test Signals
Unicode path tests, invalid encoding tests, allocation failure, and round-trip conversion coverage are important.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_utf8.c -->
