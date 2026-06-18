# sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fs_remove_rename.cpp

## Purpose
Tests live-restore `fs_remove` and `fs_rename`, especially tombstone creation while background migration is active and no-tombstone behavior after live restore completes.

## Important APIs, Types, And Functions
`stop_file_exists` checks for `WTI_LIVE_RESTORE_STOP_FILE_SUFFIX`. Tests use `WT_FILE_SYSTEM::fs_remove`, `fs_rename`, the underlying `os_file_system` for comparison, and `WTI_LIVE_RESTORE_STATE_*`.

## Control Flow
Remove tests cover destination-only removal creating a stop file, removing missing files, source-only with existing stop failing, source-only without destination succeeding by tombstoning destination path, recreating and removing a same-name destination file, completed-state removal without tombstone, completed-state source-only failure, and source+destination removal preserving source. Rename tests cover destination-only rename creating old and new stop files, missing source failing, source-only rename rejected as `EINVAL`, rename over an existing destination, and completed-state rename without tombstones.

## State And Persistence Behavior
During background migration, stop files persist logical deletion/rename intent in the destination so source files do not reappear. Source files are not removed. After live restore is complete, remove/rename operate like normal file-system calls without generating tombstones.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, stop-file suffix constants, live-restore file-system methods, and underlying OS file-system methods.

## Risks And Edge Cases
Risks include exposing deleted source files, removing source data by mistake, failing to tombstone rename destinations, and producing tombstones after completion. Rename source-only returns `EINVAL`, which distinguishes live-restore logical constraints from OS ENOENT behavior.

## Test Signals
Return codes, physical existence checks, tombstone existence checks, and source preservation checks verify expected behavior.
