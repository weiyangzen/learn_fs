# sources/storage-engines/badger/dir_unix.go

## Purpose
`dir_unix.go` is the default non-Windows, non-Plan9, non-JS/WASI, non-AIX directory locking implementation. It uses `flock` on an open directory file and fsyncs directories for crash-safe metadata updates.

## Important APIs, Types, and Functions
- `directoryLockGuard`: holds the flocked directory file, absolute pid-file path, and read-only mode.
- `acquireDirectoryLock`: opens the directory, applies exclusive or shared nonblocking `unix.Flock`, writes pid file for read-write locks, and returns a guard.
- `(*directoryLockGuard).release`: removes pid file for read-write locks and closes the directory file to release flock.
- `openDir`, `syncDir`: open a directory and call `Sync`, wrapping errors.

## Control Flow and State
The open DB path calls `acquireDirectoryLock` for the data/value directories. Read-write mode uses `LOCK_EX|LOCK_NB`; read-only uses `LOCK_SH|LOCK_NB`, allowing multiple readers but excluding writers. Releasing removes the advisory pid file before closing the flocked directory handle.

## Persistence Behavior
`syncDir` fsyncs directory entries after file creation, deletion, or rename. This is important for manifest/key-registry/table-file durability across crashes.

## Dependencies and Integration Points
This file depends on `golang.org/x/sys/unix`, `os`, `filepath`, and `y.Wrapf`. It is used by DB open/close, key-registry rewrite directory sync, and any path that needs durable directory metadata.

## Risks and Edge Cases
Locking is advisory and depends on all users respecting the same mechanism. Read-only shared locking only works on platforms selected by this file. If pid-file removal fails, release returns that error even if close succeeds.

## Test Signals
`TestPidFile`, `TestReadOnly`, and reopen/read-only tests exercise this behavior on Unix-like CI. Directory fsync errors are indirectly tested through successful DB open/close and registry rewrite paths.
