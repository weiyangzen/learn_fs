# sources/storage-engines/rocksdb/env/fs_readonly.h

## Purpose
Declares `ReadOnlyFileSystem`, a simple `FileSystemWrapper` that blocks write-like operations while forwarding read-only operations through the base wrapper. It is intended to provide a read-only filesystem view, though the comments explicitly say it has not been fully analyzed as a security boundary.

## Important APIs and Types
- `ReadOnlyFileSystem : FileSystemWrapper` with `Name()` returning `ReadOnlyFileSystem`.
- `FailReadOnly()` builds a non-retryable `IOStatus::IOError("Attempted write to ReadOnlyFileSystem")`.
- Overridden mutating operations include writable/random-RW file creation, directory creation object creation, delete/create/delete dir, rename, link, sync, lock, and logger creation.
- `CreateDirIfMissing` is special-cased to return OK if the directory already exists and is a directory.

## Control Flow
All blocked operations immediately return `FailReadOnly()` without invoking the target filesystem. `CreateDirIfMissing` calls `IsDirectory` first; if the path is an existing directory, it allows the call as a no-op, otherwise it fails as read-only.

## State and Persistence
The wrapper stores only the base filesystem through `FileSystemWrapper`. It should not create, delete, link, sync, lock, or write files through its overrides. Read-only operations not overridden are forwarded to the target.

## Dependencies and Integration Points
Depends on `rocksdb/file_system.h`. It integrates anywhere RocksDB accepts a `FileSystem` and a caller wants to prevent writes at the abstraction layer, such as read-only DB opens or tests.

## Risks and Edge Cases
- Not a hard security sandbox; operations not overridden by this wrapper may still expose behavior inherited from `FileSystemWrapper`.
- `LockFile` is blocked, which can affect code paths that use locks even for read-only coordination.
- `CreateDirIfMissing` depends on the target `IsDirectory` result; permission or path errors become read-only failures rather than preserving the original status.

## Test Signals
No direct tests are listed. Useful tests should assert every mutating override fails, `CreateDirIfMissing` succeeds for an existing directory, and ordinary read operations still pass through.
