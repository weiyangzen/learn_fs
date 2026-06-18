<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/file_lock_windows.go -->
# sources/storage-engines/pebble/vfs/file_lock_windows.go

## Purpose
Implements `vfs.Default.Lock` on Windows using exclusive `CreateFile` access.

## Important APIs, Types, and Functions
`lockCloser` wraps a Windows handle and closes it with `windows.Close`. `defaultFS.Lock` creates/truncates the file with read/write access and share mode zero.

## Control Flow
The path is converted to UTF-16. `windows.CreateFile` is called with `GENERIC_READ|GENERIC_WRITE`, no sharing, and `CREATE_ALWAYS`. A successful handle represents the lock until closed.

## State and Persistence Behavior
The lock file is created or truncated. The OS handle enforces exclusivity, including against the same process if the file is already open.

## Dependencies and Integration Points
Used by `vfs.Default.Lock` under Windows and covered by the cross-platform locking tests. It supports Pebble DB directory locking on Windows.

## Risks and Edge Cases
Because `CREATE_ALWAYS` truncates, callers must only use empty lock files. The test file explicitly rejects non-empty targets. Windows locking fails if the current process already has the file open, so callers must close temp handles before locking.

## Test Signals
`file_lock_test.go` validates the public lock contract on Windows as part of the same tests used for Unix.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/file_lock_windows.go -->
