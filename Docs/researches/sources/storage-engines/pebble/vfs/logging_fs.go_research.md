<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/logging_fs.go -->
# sources/storage-engines/pebble/vfs/logging_fs.go

## Purpose
Provides a lightweight VFS wrapper that logs filesystem and file operations. It is useful for tests and diagnostics that need to observe VFS behavior without changing the underlying filesystem.

## Important APIs, Types, and Functions
`WithLogging` wraps an `FS` with a `LogFn`. `loggingFS` implements selected `FS` methods with log lines. `loggingFile` wraps opened files and logs close, sync, sync-to, read-at, write-at, and prefetch operations.

## Control Flow
Each logging FS method emits a formatted message before delegating. Methods that return files wrap them in `loggingFile`. Open logs include option type names when options are present. `Unwrap` exposes the underlying FS for `vfs.Root`.

## State and Persistence Behavior
The wrapper stores only the log callback and file name. It does not alter persistence semantics; all durable behavior is delegated to the wrapped FS and file.

## Dependencies and Integration Points
Integrates with the `vfs.FS`/`vfs.File` interfaces and root-unwrapping behavior. It complements datadriven VFS tests and other wrappers such as error injection and syncing.

## Risks and Edge Cases
It logs before the operation, so logs may show attempted operations that later fail. It does not log every file method, such as sequential `Read`, `Write`, `Stat`, `Preallocate`, `Flush`, or `Fd`, so it is not a complete audit trail.

## Test Signals
No direct test file in this shard, but similar logging behavior is embedded in `vfs_test.go`'s `vfsTestFS` harness.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/logging_fs.go -->
