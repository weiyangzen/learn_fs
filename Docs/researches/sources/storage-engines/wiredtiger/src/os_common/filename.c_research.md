# sources/storage-engines/wiredtiger/src/os_common/filename.c

## Purpose
Provides common path construction, conditional removal, and safe copy-and-sync behavior for WiredTiger files.

## Important APIs, Types, and Functions
Functions include `__wt_filename`, `__wt_filename_construct`, `__wt_remove_if_exists`, and exported `__wt_copy_and_sync`. Private `__nfilename` joins relative names to the connection home while preserving absolute paths.

## Control Flow
`__wt_filename` delegates to `__nfilename`, which handles `NULL` sessions and absolute names by duplicating the input. Generated names append a prefix and optional zero-padded identifiers. `__wt_remove_if_exists` checks existence and refuses removal on read-only connections. `__wt_copy_and_sync` removes existing target/temp files, opens source and exclusive temp destination, copies in 128 KiB chunks, fsyncs the temp file, closes both handles, and renames temp into place.

## State and Persistence Behavior
Path helpers allocate caller-owned strings or buffers. Remove and copy paths modify the filesystem; copy uses a temp file plus fsync and durable rename to avoid leaving a silently corrupted target.

## Dependencies and Integration Points
The file depends on path separator/absolute-path helpers, allocation, file-system exists/remove/rename, `WT_FH` open/read/write/fsync/close, and stream-safe scratch buffers. Backup and tooling code use `__wt_copy_and_sync`.

## Risks and Edge Cases
`__wt_remove_if_exists` returns `EACCES` for read-only homes even if the caller expected cleanup. `__wt_copy_and_sync` removes the original target before a successful copy; recovery relies on the temp name and caller context. Name construction resets the buffer only when a non-empty path is supplied, so callers must understand append behavior.

## Test Signals
Tests should cover absolute and relative paths, `NULL` session use by test utilities, read-only remove failures, copy of empty and large files, interruption before rename, and target replacement semantics.
