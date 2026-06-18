# sources/storage-engines/badger/dir_windows.go

## Purpose
`dir_windows.go` implements Badger directory open, locking, and sync behavior on Windows. It uses a temporary delete-on-close lock file because Windows lacks the Unix flock model used elsewhere.

## Important APIs, Types, and Functions
- `openDir`, `openDirWin`: open directories using `CreateFile` with `FILE_FLAG_BACKUP_SEMANTICS`.
- `directoryLockGuard`: stores a Windows handle and lock path.
- `acquireDirectoryLock`: rejects read-only with `ErrWindowsNotSupported`, creates a lock file with no sharing and delete-on-close semantics, and returns a guard.
- `(*directoryLockGuard).release`: closes the handle, which releases and deletes the lock file.
- `syncDir`: no-op because Windows does not support directory fsync through this path.

## Control Flow and State
Lock acquisition computes an absolute lock path and calls `CreateFile` with zero access/share and `OPEN_ALWAYS`. Failure indicates another process holds the lock. Release clears the path and closes the handle.

## Persistence Behavior
No pid text is written; the lock file is temporary and deleted when the handle closes. Directory sync is intentionally a no-op, so crash-safety depends on Windows filesystem behavior and explicit file flushes elsewhere.

## Dependencies and Integration Points
Selected by the `windows` build tag. It integrates with Badger open/close lock acquisition and uses `syscall`, `os.NewFile`, and Badger error wrapping.

## Risks and Edge Cases
Read-only mode is unsupported on Windows. Directory metadata is not fsynced. The lock-file mechanism is simpler than `LockFileEx` and relies on `CreateFile` sharing behavior.

## Test Signals
`TestWindowsDataLoss` is Windows-specific and exercises mmap/reopen behavior, while read-only tests expect `ErrWindowsNotSupported`. Lock behavior is covered indirectly by DB open tests on Windows.
