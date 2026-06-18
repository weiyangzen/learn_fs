# sources/storage-engines/badger/dir_plan9.go

## Purpose
`dir_plan9.go` implements Badger directory locking and syncing for Plan 9. It uses Plan 9's exclusive-use file semantics instead of flock and explicitly rejects read-only mode.

## Important APIs, Types, and Functions
- `directoryLockGuard`: stores the locked pid file handle and absolute path.
- `acquireDirectoryLock`: rejects read-only with `ErrPlan9NotSupported`, ensures the pid file has `os.ModeExclusive`, opens it exclusively, and writes the pid.
- `(*directoryLockGuard).release`: removes the pid file, closes the file handle, and clears guard state.
- `openDir`, `syncDir`: open and fsync a directory.
- `lockedErrStrings`, `isLocked`: classify Plan 9 lock-related error text.

## Control Flow and State
Lock acquisition first normalizes the pid path, updates an existing pid file's exclusive bit when needed, and then relies on `os.OpenFile` with `os.ModeExclusive` to fail if another process has the file open. Release removes the pid file before closing the handle.

## Persistence Behavior
The pid file persists while the DB is open and records the process id. `syncDir` fsyncs the directory for metadata durability where supported by Plan 9's filesystem.

## Dependencies and Integration Points
This platform implementation plugs into Badger open/close via the same functions used by Unix and Windows implementations. It depends on `os`, `filepath`, string error matching, and `y.Wrap`.

## Risks and Edge Cases
Plan 9 read-only DB mode is unsupported. Lock detection depends on known error substrings from Plan 9 filesystems; an unfamiliar filesystem error could be misclassified. Cleanup ordering intentionally removes the pid file before closing the exclusive handle.

## Test Signals
Shared tests like `TestReadOnly` should observe `ErrPlan9NotSupported` on Plan 9. There are no dedicated unit tests for `isLocked` or exclusive-bit repair.
