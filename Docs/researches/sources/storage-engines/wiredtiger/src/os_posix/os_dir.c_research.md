# sources/storage-engines/wiredtiger/src/os_posix/os_dir.c

## Purpose
Implements POSIX directory listing for WiredTiger's file-system abstraction.

## Important APIs, Types, and Functions
`__wti_posix_directory_list` returns all matching entries, `__wti_posix_directory_list_single` returns at most one, and `__wti_posix_directory_list_free` frees the returned array. Private `__directory_list_worker` contains the shared `opendir`/`readdir`/`closedir` logic.

## Control Flow
The worker opens the directory with syscall retry, captures diagnostic messages with timestamps and directory file descriptors, iterates entries skipping `.` and `..`, filters by optional prefix, duplicates matching names into a growing array, and stops early for single-entry mode. It detects `readdir` failure via `errno`, closes the directory, and on close errors prints captured open/read diagnostics.

## State and Persistence Behavior
The function allocates a caller-owned array of duplicated entry names. It does not modify the filesystem.

## Dependencies and Integration Points
It depends on POSIX `DIR`, `opendir`, `readdir`, `closedir`, `dirfd`, WiredTiger scratch buffers, allocation helpers, and the `WT_FILE_SYSTEM` directory-list ABI.

## Risks and Edge Cases
Directory entries are returned as names relative to the directory, not full paths. The prefix filter applies only to `d_name`. Errors after partial allocation must free every duplicated entry. Close errors are rare but heavily diagnosed because past failures were hard to debug.

## Test Signals
Filesystem tests should cover empty directories, prefix filtering, single-entry mode, large directories that force realloc, opendir/readdir/closedir failures, and freeing partial results.
