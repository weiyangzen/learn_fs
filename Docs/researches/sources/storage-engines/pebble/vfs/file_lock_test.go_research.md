<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/file_lock_test.go -->
# sources/storage-engines/pebble/vfs/file_lock_test.go

## Purpose
Tests exclusive lock behavior for `vfs.Default.Lock` across processes and within one process.

## Important APIs, Types, and Functions
`TestLock` uses a `-lockfile` flag to run as parent or child process. `spawn` reinvokes the test binary. `TestLockSameProcess` checks that re-locking the same file in one process fails.

## Control Flow
The parent creates an empty temp file, locks it, spawns a child that should fail to lock it, closes the lock, then spawns another child that should succeed. The child path simply tries to lock the provided file and exits through test success/failure. The same-process test locks once, attempts a second lock, expects an error, and releases the first lock.

## State and Persistence Behavior
Temporary lock files are created, truncated by platform lock implementations, and removed by the parent. The tests enforce that non-empty files are not accidentally used as lock files.

## Dependencies and Integration Points
Covers `file_lock_unix.go` and `file_lock_windows.go` through the public `vfs.Default` FS interface. It validates behavior relied on by Pebble DB directory locking.

## Risks and Edge Cases
The test depends on subprocess execution and platform-specific lock semantics. On Windows, files must be closed before locking; the test explicitly closes the temp file before calling `Lock`.

## Test Signals
Passing confirms interprocess exclusion, lock release on `Close`, and same-process duplicate lock rejection.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/file_lock_test.go -->
