# sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fs_exist.cpp

## Purpose
Tests `fs_exist` in live restore across every combination of destination presence, source presence, migration state, and destination tombstone presence.

## Important APIs, Types, And Functions
`file_exists` calls `WTI_LIVE_RESTORE_FS::iface.fs_exist` on the destination-path form visible to WiredTiger. `test_file_exists` prepares combinations using `HasDest`, `HasSource`, `IsMigrating`, and `HasStop`.

## Control Flow
For each permutation, existing artifacts are removed, destination/source/stop files are created as requested, the live-restore state is set to background migration or complete, and `fs_exist` is called. The test then asserts the expected boolean result.

## State And Persistence Behavior
Destination files always make the logical file exist. Source-only files exist only while background migration is active and no tombstone exists. Once migration is complete, source-only files are invisible because they should have been copied already.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, live-restore state constants, and stop-file suffix behavior.

## Risks And Edge Cases
The complete 16-permutation matrix guards against regressions where tombstones are ignored, completed migration still exposes source-only files, or destination files are hidden by tombstones.

## Test Signals
The expected booleans are the signal: all no-file cases false, source-only migrating without stop true, source-only with stop false, and all destination-present cases true.
