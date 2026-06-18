# sources/storage-engines/wiredtiger/test/catch2/live_restore/live_restore_test_env.cpp

## Purpose
Implements the shared live-restore Catch2 test environment. It creates a valid WiredTiger backup-like source directory, reopens the destination with live restore enabled, and exposes path helpers for destination, source, and tombstone files.

## Important APIs, Types, And Functions
`live_restore_test_env::live_restore_test_env` removes old `WT_LR_DEST` and `WT_LR_SOURCE`, creates a non-live-restore database, opens a `backup:` cursor, copies listed files into source, removes destination, then opens a live-restore connection with `live_restore=(enabled=true,path=WT_LR_SOURCE,threads_max=0),statistics=(fast)`. `dest_file_path`, `source_file_path`, and `tombstone_file_path` build backing paths.

## Control Flow
Construction has two phases: create and copy a baseline backup, then reopen using live restore. The backup cursor yields URIs that are copied from destination to source. After the live-restore connection opens, the environment stores `session` and casts the connection file system to `WTI_LIVE_RESTORE_FS`.

## State And Persistence Behavior
The fixture creates and deletes real directories under the test working directory. Source persists as the backup input; destination is recreated as the live database home. Migration threads are disabled, giving tests direct control over migration effects.

## Dependencies And Integration Points
Depends on `live_restore_test_env.h`, `connection_wrapper`, `testutil_remove`, `testutil_mkdir`, `testutil_copy`, backup cursors, and live-restore configuration.

## Risks And Edge Cases
The fixture assumes backup cursor entries can be copied directly and that test names do not collide outside the fixed `WT_LR_*` directories. Manual file manipulation in tests relies on `threads_max=0` to prevent background interference.

## Test Signals
The constructor uses `REQUIRE` on session, cursor, key retrieval, and copy steps. Any environment setup regression fails before individual live-restore tests run.
