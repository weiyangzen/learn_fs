# sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fs_open_file.cpp

## Purpose
Tests live-restore `fs_open_file` for regular files and directories. It verifies creation, source-to-destination materialization, nested source paths, tombstone rejection, and directory-only destination semantics.

## Important APIs, Types, And Functions
`open_file` wraps `WTI_LIVE_RESTORE_FS::iface.fs_open_file` and checks the expected return. `validate_lr_fh` checks destination handle presence, optional source/bitmap absence for directories, destination name, and `back_pointer`.

## Control Flow
The regular-file section checks ENOENT for missing files, destination creation with `WT_FS_OPEN_CREATE`, opening destination-only files, source-only files that create a destination copy, nested source files with automatic destination subdirectory creation, files in both locations, and tombstoned source files returning ENOENT. The directory section checks missing directories and source-only directories return ENOENT, while destination-present directories open successfully with no source handle or bitmap.

## State And Persistence Behavior
Opening a source-only regular file creates a destination-side file and any needed destination subdirectories. Directory opens do not create destination directories because WiredTiger expects directories to be created outside this path. Tombstones in destination suppress source files.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, `WT_FS_OPEN_FILE_TYPE_REGULAR`, `WT_FS_OPEN_FILE_TYPE_DIRECTORY`, and live-restore handle internals.

## Risks And Edge Cases
Risks include creating directories in cases where WiredTiger should not, failing to create nested destination paths for source files, ignoring tombstones, and leaving invalid source or bitmap state for directory handles.

## Test Signals
Expected return codes (`0` or `ENOENT`), destination existence checks, handle fields, and source/bitmap nullness for directories provide coverage.
