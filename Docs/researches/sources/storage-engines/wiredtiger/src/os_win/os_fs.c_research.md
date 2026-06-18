<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_fs.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_fs.c

## Purpose
Implements Windows `WT_FILE_SYSTEM` and file-handle operations for create/open, read/write, sync, size, rename/remove, locking, mapping hooks, and free-space queries.

## Important APIs, Types, and Functions
`__wt_os_win` installs the file-system jump table. `__win_open_file`, `__win_file_read`, `__win_file_write`, `__win_file_sync`, `__win_file_set_end`, `__win_file_lock`, `__win_fs_remove`, `__win_fs_rename`, and `__wti_win_fs_size` implement core operations. `WT_WINCALL_RETRY` retries access-denied operations.

## Control Flow
Path-taking operations convert UTF-8 to UTF-16. Open maps WiredTiger flags to `CreateFileW` access, share, disposition, write-through, random/sequential hints, and opens a secondary handle for truncation/extension. I/O uses `ReadFile`/`WriteFile` with `OVERLAPPED` offsets and 1GB chunks. Remove/rename retry transient `ERROR_ACCESS_DENIED`, useful for virus scanners. Rename uses `MoveFileExW` with replacement and write-through.

## State and Persistence Behavior
`FlushFileBuffers` provides file flushes; Windows directory handles are not opened for durability. Secondary handles allow file-size changes without moving the main I/O pointer. No WiredTiger metadata is persisted directly.

## Dependencies and Integration Points
Uses UTF conversion, Windows error mapping, directory-list hooks, map/unmap hooks, log sync configuration, connection write-through flags, and standard WiredTiger allocation/error macros.

## Risks and Edge Cases
Create flag handling is easy to misread: exclusive/create disposition behavior needs tests. Windows rename is not documented as atomic across all cases, so code avoids copy fallback. Secondary-handle failures disable truncate/extend. Access-denied retries can mask external interference only briefly.

## Test Signals
Windows filesystem tests should cover Unicode paths, open/create/exclusive combinations, concurrent extension with reads, rename/remove under sharing conflicts, free-space queries, and write-through/sync behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_fs.c -->
