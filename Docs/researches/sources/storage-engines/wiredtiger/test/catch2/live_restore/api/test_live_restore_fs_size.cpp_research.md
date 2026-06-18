# sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fs_size.cpp

## Purpose
Tests live-restore file-system-level `fs_size` over all combinations of destination file, source file, migration state, and tombstone file.

## Important APIs, Types, And Functions
`file_size` calls `WTI_LIVE_RESTORE_FS::iface.fs_size` on a destination-path file name. `test_file_size` prepares the four-factor state matrix with `DEST_FILE_SIZE`, `SOURCE_FILE_SIZE`, and live-restore state constants.

## Control Flow
The test removes stale files, conditionally creates destination/source/stop files, sets migration state, calls `fs_size`, and verifies return code and size. It enumerates all relevant permutations.

## State And Persistence Behavior
Destination is authoritative when present. Source-only files are visible and sized from source only during background migration and only if no stop file exists. Completed migration hides source-only files. Tombstones make source-only files look absent.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, live-restore file-system API, and stop-file naming.

## Risks And Edge Cases
The matrix catches divergence between `fs_exist` and `fs_size` semantics, including source visibility after completion, stop-file suppression, and destination precedence over source.

## Test Signals
Expected `ENOENT` or `0` return plus exact size (`SOURCE_FILE_SIZE` or `DEST_FILE_SIZE`) is asserted for each case.
