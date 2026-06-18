# sources/storage-engines/rocksdb/env/fs_posix.cc

## Purpose
Implements RocksDB's default non-Windows `FileSystem` on top of POSIX APIs. It creates the concrete file classes from `io_posix.{h,cc}`, implements metadata operations, locks, directory operations, direct-I/O/mmap/io_uring feature selection, path registration for logical block-size caching, and registers the `posix://` filesystem factory.

## Important APIs and Types
- Anonymous `PosixFileSystem : FileSystem` implements `NewSequentialFile`, `NewRandomAccessFile`, `OpenWritableFile`, `NewWritableFile`, `ReopenWritableFile`, `ReuseWritableFile`, `NewRandomRWFile`, `NewMemoryMappedFileBuffer`, `NewDirectory`, and metadata operations.
- `PosixFileLock` and `LockOrUnlock` implement process-level lock handling with a process-local `locked_files` map.
- `OptimizeForLogWrite`, `OptimizeForManifestWrite`, and `OptimizeForCompactionTableRead` adjust `FileOptions`.
- `RegisterDbPaths`/`UnregisterDbPaths` manage Linux logical block-size cache references.
- `Poll`, `AbortIO`, and `SupportedOps` expose optional io_uring async I/O support.
- `FileSystem::Default()` returns a singleton `PosixFileSystem`; object registry adds a `posix://` factory.

## Control Flow
File-open methods build POSIX flags from `FileOptions`, retry `open` on `EINTR`, set close-on-exec, then instantiate a matching `io_posix` class. Direct reads/writes use `O_DIRECT` except on platform-specific alternatives; macOS uses `F_NOCACHE`, Solaris can call `directio`. mmap reads map the full opened file; mmap writes are disabled once if the backing filesystem does not support fast allocation. `ReuseWritableFile` opens the old file, renames it into the target name, and wraps the already-open descriptor. Metadata operations map directly to `access`, `opendir/readdir/closedir`, `unlink`, `mkdir`, `rmdir`, `stat`, `rename`, `link`, `statvfs`, `open/fstat`, and related POSIX calls. Async `Poll` waits for io_uring CQEs and finalizes matching handles; `AbortIO` submits cancel SQEs and waits for original plus cancel completions for aborted handles.

## State and Persistence
Persistent effects include file creation/truncation, renames, links, deletes, directory creation/removal, advisory locks, mmap writes, preallocation, and syncs. Runtime process state includes `locked_files`, `forceMmapOff_`, `page_size_`, `allow_non_owner_access_`, optional thread-local io_uring rings, and the static Linux `LogicalBlockSizeCache`. The default filesystem singleton persists for process lifetime.

## Dependencies and Integration Points
Depends on `env/io_posix.h` classes, `monitoring/iostats_context_imp.h`, RocksDB options, `ObjectLibrary`, sync points, thread-local helpers, and many POSIX/kernel headers. It is the primary integration point between RocksDB's abstract `FileSystem` API and platform storage. It also plugs into the object registry for URI-based construction.

## Risks and Edge Cases
- `GetAbsolutePath` returns the current working directory for any relative DB path without appending the relative path; callers expecting a full absolute path must account for this behavior.
- `FileExists` maps several access errors, including `EACCES`, to `NotFound`, which can hide permission problems behind existence checks.
- `OpenWritableFile` with reopen uses `O_CREAT | O_APPEND` without `O_WRONLY` in the non-direct/non-mmap path until the later branch adds only for alternatives; this relies on platform flag behavior and deserves scrutiny.
- Locking must maintain the process-local map before opening because POSIX locks are per-process; incorrect removal would release locks unexpectedly.
- Async io_uring support is gated by compile-time support, a weak `RocksDbIOUringEnable()` hook, constructor probing, and per-thread initialization. Any ring mismatch returns generic `IOError("")` in some paths.
- mmap write support is disabled globally after a one-time filesystem probe on the default filesystem.

## Test Signals
`io_posix_test.cc` indirectly exercises the default filesystem for writable truncate/append seek behavior and directory fsync behavior through `FileSystem::Default()`. Other RocksDB env tests likely cover metadata and locking. Important gaps for this file are `ReuseWritableFile`, `GetAbsolutePath`, URI factory construction, io_uring `Poll`/`AbortIO`, direct-I/O flag selection, and logical block-size registration lifecycle.
