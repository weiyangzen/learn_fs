# sources/storage-engines/badger/dir_other.go

## Purpose
`dir_other.go` provides directory locking and syncing for `js` and `wasip1` builds, where normal OS-level flock support is unavailable.

## Important APIs, Types, and Functions
- `directoryLockGuard`: holds an open directory file, absolute pid-file path, and read-only flag.
- `acquireDirectoryLock`: opens the directory, skips actual flocking, writes pid file for read-write mode, and returns a guard.
- `(*directoryLockGuard).release`: removes pid file for read-write locks and closes the directory handle.
- `openDir`, `syncDir`: open and fsync a directory path using `os.File.Sync`.

## Control Flow and State
Acquisition resolves the pid path, opens the directory, and deliberately avoids flock calls. For read-write mode it overwrites the pid file. Release removes the pid file before closing the directory handle.

## Persistence Behavior
The pid file is advisory only and is not backed by an exclusive kernel lock in these targets. `syncDir` attempts to fsync directory entries, returning wrapped open/sync/close errors.

## Dependencies and Integration Points
Selected by `js || wasip1` build tags. It supports the same Badger open/close integration points as other `dir_*` files, allowing the rest of the codebase to call `acquireDirectoryLock`, `release`, and `syncDir` uniformly.

## Risks and Edge Cases
The absence of real locking means concurrent writers are not prevented by this implementation. Environments with limited filesystem support may also make `os.Open`, pid writes, or `Sync` behave differently than POSIX hosts.

## Test Signals
No target-specific tests are present. General DB locking tests would not fully validate the missing flock behavior unless run in JS/WASI-like environments.
