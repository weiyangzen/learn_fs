# sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fh_size.cpp

## Purpose
Verifies that a live-restore file handle's `fh_size` always reports the destination file size once the file has been opened, regardless of source presence, migration state, or tombstone file presence.

## Important APIs, Types, And Functions
`fh_size_wrapper` opens a data file through `WTI_LIVE_RESTORE_FS::iface.fs_open_file`, calls `WTI_LIVE_RESTORE_FILE_HANDLE::iface.fh_size`, and closes it. `test_fh_size` prepares `DEST/SOURCE`, `MIGRATING/NOT_MIGRATING`, and `STOP/NO_STOP` cases using `WTI_LIVE_RESTORE_STATE_*` and `WTI_LIVE_RESTORE_STOP_FILE_SUFFIX`.

## Control Flow
For each permutation, the helper removes old test files, creates a destination file of size 10, optionally creates a source file of size 100, sets migration state, optionally creates a stop file, opens the handle, reads size, and asserts it is the destination size.

## State And Persistence Behavior
The destination file is the authoritative size once opened. Source and tombstone files only affect open/existence decisions elsewhere, not this handle-level size path.

## Dependencies And Integration Points
Depends on `utils_live_restore.h` and the shared live-restore environment. It integrates with file-handle open and size methods.

## Risks And Edge Cases
Covers all boolean combinations of source, migration, and stop file while destination exists. It intentionally does not test absent destination because open either creates it or fails before handle-level `fh_size`.

## Test Signals
Every permutation must return `DEST_FILE_SIZE`. Any source-size or tombstone-driven result indicates a regression in handle-level size semantics.
