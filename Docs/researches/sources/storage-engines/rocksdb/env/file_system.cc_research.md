# sources/storage-engines/rocksdb/env/file_system.cc

## Purpose

`file_system.cc` implements core default behavior for the `FileSystem` abstraction: built-in factory registration, string-based construction, convenience helpers for writing and reading whole files, default `SyncFile`, default logger creation, file-option optimization hooks, wrapper option serialization, and `DirFsyncOptions` constructors.

## Important APIs, types, and functions

- `RegisterBuiltinFileSystems()` registers `TimedFileSystem`, `ReadOnlyFileSystem`, `EncryptedFileSystem`, `CountedFileSystem`, `MockFileSystem`, and non-Windows `ChrootFileSystem` with `ObjectLibrary`.
- `FileSystem::CreateFromString()` returns `FileSystem::Default()` when the string names the default; otherwise it registers built-ins once and calls `LoadSharedObject<FileSystem>()`.
- `FileSystem::ReuseWritableFile()` implements the default rename-then-open behavior.
- `FileSystem::SyncFile()` reopens a writable file, calls `Sync()` or `Fsync()`, closes it, and preserves the primary sync/fsync error over a close error.
- `FileSystem::NewLogger()` creates an `EnvLogger` over a new writable file with a default 1 MiB writable-file buffer.
- `OptimizeForLogRead()`, `OptimizeForManifestRead()`, `OptimizeForLogWrite()`, `OptimizeForManifestWrite()`, `OptimizeForCompactionTableWrite()`, `OptimizeForCompactionTableRead()`, and `OptimizeForBlobFileRead()` adjust `FileOptions` based on DB options.
- `WriteStringToFile()` writes a full slice, optionally syncs, explicitly closes, and deletes the file on failure.
- `ReadFileToString()` reads a sequential file in 8192-byte chunks into a `std::string`.
- `FileSystemWrapper::PrepareOptions()` fills a null target with `FileSystem::Default()`.
- `FileSystemWrapper::SerializeOptions()` includes a `target=` option for non-default targets unless shallow serialization is requested.
- `DirFsyncOptions` constructors encode default, rename, and explicit fsync reasons.

## Control flow

`CreateFromString()` first checks whether the default file system already matches the requested value. If not, a `std::once_flag` registers built-in factories in the default object library, then shared-object loading handles registry/config parsing. Built-in wrappers are generally created with null targets; their `PrepareOptions()` later fills in `FileSystem::Default()` through wrapper behavior.

`SyncFile()` opens the file with `ReopenWritableFile()`. A sync point can observe or modify the open status. On success it calls either `Fsync()` or `Sync()`, always attempts `Close()`, and returns the close status only if the sync/fsync path succeeded. If sync/fsync failed, the close error is marked checked and suppressed.

`WriteStringToFile()` opens a writable file, appends all data, syncs if requested, then explicitly closes. This avoids relying on destructors that could hide close/flush errors. Any error after file creation triggers `DeleteFile()` cleanup. `ReadFileToString()` opens a sequential file with default options and loops until a read error or an empty fragment signals EOF.

Option optimization methods copy the input `FileOptions` and change only the relevant fields: log/manifest reads disable direct reads, log writes inherit WAL bytes-per-sync and writable buffer size, compaction/blob reads use direct-read DB options, and compaction table writes use direct-write DB options.

## State and persistence behavior

This file owns no long-lived mutable state other than one-time built-in factory registration. It affects persistent data through helper methods: `ReuseWritableFile()` renames files, `WriteStringToFile()` creates/replaces file content and deletes failed writes, `ReadFileToString()` loads content into memory, and `SyncFile()` flushes existing file data to storage. Wrapper serialization preserves target file-system topology in option strings when the target is non-default.

## Dependencies and integration points

The file integrates with `env_encryption.cc` through `NewEncryptedFileSystemImpl()`, with `Env::Default()` for logger creation and default targets, with object registry/customizable option infrastructure, and with built-in wrappers from `env_chroot`, `fs_readonly`, `mock_env`, `counted_fs`, and `env_timed`. Tests in `env_test.cc` cover factory creation for all registered built-ins, read/write helpers, and `SyncFile` error ordering.

## Risks and edge cases

- `ReadFileToString()` allocates its buffer with `new[]` and deletes it manually; early returns are avoided, but RAII would be safer.
- `ReadFileToString()` wraps `NewSequentialFile()` with `status_to_io_status()` even though it already returns `IOStatus` in this API layer, which is harmless but signals historical API layering.
- `WriteStringToFile()` deletes the destination on any append/sync/close failure. That is appropriate for helper semantics but important for callers that expect partial files to remain for diagnostics.
- `SyncFile()` requires a functioning `ReopenWritableFile()` implementation. File systems that do not support reopening writable files inherit a default that may return errors.
- Factory-created wrappers with null targets depend on `PrepareOptions()` being invoked before operational use.
- `SerializeOptions()` suppresses default targets and shallow targets; tooling that expects fully explicit target chains must request non-shallow serialization.

## Test signals

`env_test.cc` includes `CreateReadOnlyFileSystem`, `CreateTimedFileSystem`, `CreateCountedFileSystem`, `CreateChrootFileSystem`, and `CreateEncryptedFileSystem` for factory/serialization behavior. `WriteStringToFileClosesFile` verifies explicit close, and `WriteStringToFileCloseFailureDeletesFile` verifies cleanup on close error. `FileSystemSyncFileDefaultUsesSyncAndFsync`, `FileSystemSyncFileDefaultReturnsReopenError`, `FileSystemSyncFileDefaultReturnsCloseErrorAfterSuccessfulSync`, and `FileSystemSyncFileDefaultReturnsSyncErrorBeforeCloseError` validate `SyncFile()` call order and error precedence.
