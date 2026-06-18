# sources/storage-engines/rocksdb/include/rocksdb/env.h

## Purpose

`env.h` defines RocksDB's historical public abstraction over the operating system environment. It covers file creation/opening, file IO primitives, directory and lock operations, dynamic library loading, logging, background thread pools, clocks, test directories, and helper wrappers. The top-level contract says `Env` implementations are safe for concurrent access, while individual returned file objects document their own synchronization rules. It is the compatibility bridge for older Env-based integrations and for newer FileSystem/SystemClock composition through `NewCompositeEnv`.

## Important APIs, types, and functions

The central type is `Env : public Customizable`, with factory/load entry points `Env::Default()`, `CreateFromString()`, and `CreateFromUri()`. `EnvOptions` carries file-open and IO tuning flags such as mmap, direct IO, fallocate, `bytes_per_sync`, `strict_bytes_per_sync`, write buffering, and rate limiting.

File abstractions are `SequentialFile`, `RandomAccessFile`, `WritableFile`, `RandomRWFile`, `MemoryMappedFileBuffer`, and `Directory`. They expose operations such as `Read`, `Skip`, `MultiRead`, `Append`, `PositionedAppend`, `Flush`, `Sync`, `Fsync`, `Truncate`, `InvalidateCache`, `Allocate`, and unique-id retrieval. `ReadRequest` represents batched random read inputs and per-request statuses. Logging is modeled by `Logger`, `InfoLogLevel`, free functions `Log`, `Info`, `Warn`, `Error`, `Fatal`, and `NewEnvLogger`. `FileLock` and `DynamicLibrary` model database locks and runtime symbol lookup.

`EnvWrapper` and the file wrappers forward calls to a target implementation, allowing partial behavioral overrides. `NewMemEnv`, `NewTimedEnv`, and `NewCompositeEnv` are extension factories.

## Control flow and behavior

DB code enters through `Env` methods to create files and directories, inspect filesystem state, lock DB paths, schedule background work, and query time. Most file open methods return owning `std::unique_ptr` objects and set `nullptr` on failure. `RandomAccessFile::MultiRead` defaults to a loop over `Read`, while `WritableFile::PrepareWrite` tracks preallocation blocks and calls `Allocate` when an append crosses a new block. `SyncFile` provides a path-level durability helper using writable reopen plus `Sync` or `Fsync` by default.

Thread control flows through `Schedule`, `UnSchedule`, `StartThread`, `StartThreadTyped`, and pool sizing calls. `StartThreadTyped` wraps typed arguments in `FunctorWrapper`, invokes the stored function inside a raw `StartThread` trampoline, then deletes the wrapper.

## State and persistence

`Env` owns optional `file_system_`, `system_clock_`, and `thread_status_updater_` pointers. `WritableFile` tracks preallocation state, IO priority, write lifetime hint, and strict range-sync behavior. Persistence semantics are explicitly layered: `Flush` makes data independent of process memory, `Sync` persists file data, `Fsync` persists metadata when overridden, and `Directory::Fsync` persists directory changes. `Close` is expected to surface final write errors, but objects still need destructor cleanup for unclosed resources.

## Dependencies and integration points

This header depends on `Customizable`, `Status`, `ThreadStatus`, `types`, `FunctorWrapper`, `FileSystem`, `SystemClock`, `DBOptions`, `ImmutableDBOptions`, `RateLimiter`, and `IOOptions`. It integrates directly with DB open options, compaction and WAL IO optimization, table file writing, logging, Env-based tests, plugin loading, and thread-status reporting. `EnvWrapper` is the key integration hook for instrumentation, encryption, rate limiting, in-memory filesystems, or partial overrides.

## Risks and test signals

The strongest risk is contract drift between base classes and wrappers; comments repeatedly require wrapper updates when methods are added. Implementations must not throw exceptions across RocksDB APIs. Direct IO users must respect alignment for offsets, lengths, and buffers. Incorrect `Flush`/`Sync`/`Fsync` semantics can lose data or metadata after crashes. `GetUniqueId` must avoid prefix ambiguity. Test signals include Env wrapper forwarding tests, direct-IO alignment and positioned append tests, crash/durability tests for `SyncFile`, background scheduling and unscheduling tests, logger level tests, and tests that default unsupported APIs return `NotSupported` without breaking callers.
