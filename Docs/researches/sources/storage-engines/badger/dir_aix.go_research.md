# sources/storage-engines/badger/dir_aix.go

## Purpose
`dir_aix.go` implements AIX-specific directory locking and directory sync abstractions for Badger. It handles AIX's file/process locking semantics, which differ from descriptor-scoped flock behavior on Unix.

## Important APIs, Types, and Functions
- `directoryLockGuard`: records the absolute pid-file path and whether the lock is read-only.
- `aixFlock`: shared process-local lock state containing one open file, reference count, and read-only mode.
- `aixFlockMap` and `aixFlockMapLock`: process-local registry preventing multiple descriptors for the same AIX lock file.
- `acquireDirectoryLock(dirPath, pidFileName, readOnly)`: creates or reuses a lock file, applies `unix.FcntlFlock`, writes pid for read-write mode, and returns a guard.
- `(*directoryLockGuard).release`: decrements refcount, removes pid file for read-write locks, closes the file, and deletes map state.
- `openDir`, `syncDir`: AIX directory open/sync adapters; `syncDir` is a no-op because AIX does not support fsync on directories.

## Control Flow and State
Lock acquisition resolves the pid path to an absolute path, locks the global map, and either reuses a compatible read-only lock or creates a new file lock. Read-write and read-only locks are mutually exclusive in the in-process map. Release is refcounted and only closes/removes the underlying file on the final release.

## Persistence Behavior
Read-write acquisition writes the process id into the pid file. Final release truncates and removes the pid file. `syncDir` intentionally does not fsync directory entries, so crash durability for file creation/removal metadata is weaker on AIX than on Unix platforms with directory fsync.

## Dependencies and Integration Points
This file is selected only by the `aix` build tag and is consumed by Badger open/close paths through `acquireDirectoryLock`, `release`, `openDir`, and `syncDir`. It depends on `golang.org/x/sys/unix`, `os`, `filepath`, `sync`, and Badger's `y.Wrapf` helpers.

## Risks and Edge Cases
The main risk is mismatch between AIX lock semantics and Badger's normal expectation that multiple descriptors can coexist. The map/refcount approach is process-local and does not replace kernel inter-process locking. The no-op directory sync can affect crash consistency of directory entries.

## Test Signals
No AIX-specific tests are in this file. Cross-platform DB locking tests such as `TestPidFile` and `TestReadOnly` exercise the shared behavior when run on AIX.
