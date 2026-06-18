# sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fh_lock_close_sync.cpp

## Purpose
Smoke-tests live-restore file-handle `fh_lock`, `fh_sync`, write+sync, and close behavior. The file deliberately avoids re-testing lower-level POSIX semantics and focuses on API forwarding through the live-restore handle wrapper.

## Important APIs, Types, And Functions
Uses `live_restore_test_env`, `create_file`, `WTI_LIVE_RESTORE_FS::iface.fs_open_file`, and `WT_FILE_HANDLE` methods `fh_lock`, `fh_sync`, `fh_write`, and `close`. It downcasts to `WTI_LIVE_RESTORE_FILE_HANDLE` to set `allocsize` before writing.

## Control Flow
The test creates matching source and destination files, opens a destination data file through the live-restore file system, locks and unlocks it, verifies re-entrant locking succeeds, syncs with no writes, writes a 4096-byte buffer, syncs again, and closes the handle.

## State And Persistence Behavior
The only persistent effect is a write to the destination backing file. Source is present to allow live-restore open behavior, but this test does not inspect migration bitmap state.

## Dependencies And Integration Points
Depends on `utils_live_restore.h` and the mock session wrapper transitively. It integrates with the live-restore file system implementation and underlying file handle operations.

## Risks And Edge Cases
The test covers re-entrant locks and sync-after-write. It does not test double-close because the implementation aborts, and it does not verify lock exclusion across threads.

## Test Signals
All file handle calls must return zero. A failure indicates live-restore wrapper forwarding, write setup, or handle lifecycle regression.
