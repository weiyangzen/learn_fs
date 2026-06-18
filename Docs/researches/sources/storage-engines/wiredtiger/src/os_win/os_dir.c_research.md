<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_dir.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_dir.c

## Purpose
Implements Windows directory listing for WiredTiger's file-system abstraction, including prefix filtering and single-result mode.

## Important APIs, Types, and Functions
`__directory_list_worker`, `__wti_win_directory_list`, `__wti_win_directory_list_single`, and `__wti_win_directory_list_free`.

## Control Flow
The worker normalizes the directory, builds a `\*` search path, converts path and prefix to UTF-16, iterates `FindFirstFileW`/`FindNextFileW`, skips `.`/`..`, applies optional prefix matching, converts matched names back to UTF-8, duplicates them into a growable array, and frees partial results on error.

## State and Persistence Behavior
No persistent state is changed. Returned file-name arrays are heap allocated and must be freed by the paired free function.

## Dependencies and Integration Points
Installed by `os_win/os_fs.c` in the Windows `WT_FILE_SYSTEM`. Relies on UTF conversion helpers and Windows error mapping.

## Risks and Edge Cases
Prefix conversion is performed even when prefix may be NULL, so correctness depends on helper/caller expectations. Errors during cleanup can overwrite return codes. Directory order is filesystem-defined.

## Test Signals
Tests should cover empty directories, prefix filters, Unicode names, single-result mode, cleanup on mid-iteration allocation failure, and Windows error mapping.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_dir.c -->
