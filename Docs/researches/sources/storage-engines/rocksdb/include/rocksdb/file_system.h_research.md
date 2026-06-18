# sources/storage-engines/rocksdb/include/rocksdb/file_system.h

## Purpose

`file_system.h` defines RocksDB's newer, IOStatus-based storage abstraction. Compared with `Env`, it separates filesystem IO from clocks and thread pools, passes per-request `IOOptions` and `IODebugContext`, supports async reads and filesystem-owned buffers, and exposes richer file-open and metadata contracts for local or remote storage systems.

## Important APIs, types, and functions

`IOOptions` carries timeout, deprecated priority, rate-limiter priority, IO type, opaque property bag, directory fsync controls, recursion controls, verify-and-reconstruct-read, and IO activity. `DirFsyncOptions` explains why a directory fsync is needed. `FileOpenContract` declares constraints such as no reopen-for-write and no readers while open for write. `FileOptions : EnvOptions` adds embedded `IOOptions`, temperature, open contract, checksum handoff type, write hint, file checksum metadata, and optional file-open metadata.

`IODebugContext` records file path, counters, message, request id, trace data, cost info, and a shared mutex for implementation-side synchronization. `FileSystem : public Customizable` is the top-level factory for `FSSequentialFile`, `FSRandomAccessFile`, `FSWritableFile`, `FSRandomRWFile`, memory-mapped buffers, directories, locks, loggers, and metadata operations. It also exposes `Poll`, `AbortIO`, `DiscardCacheForDirectory`, and `SupportedOps`.

File classes mirror `Env` classes but return `IOStatus` and accept `IOOptions` plus debug contexts. `FSReadRequest` supports synchronous `MultiRead`, asynchronous `ReadAsync`, and optional filesystem-owned buffers via `FSAllocationPtr`. Wrapper and owner-wrapper classes forward calls while optionally owning the wrapped object.

## Control flow and behavior

DB code opens files through `FileSystem` with `FileOptions`, then performs each IO with request-specific options and debug context. Default `GetChildrenFileAttributes` lists names, stats each child, and silently skips children deleted after listing. Default `FSRandomAccessFile::MultiRead` loops over `Read`; default `ReadAsync` performs synchronous read and invokes the callback before returning. `SupportedOps` defaults to async IO and prefetch support, and implementations must override it to advertise filesystem buffers or verify-and-reconstruct reads. `SyncFile` is the path-level durability hook for callers that need to sync a named file without violating file-open contracts.

## State and persistence

`FileSystem` itself has no mandated persistent state, but implementations may track DB path registration, caches, async handles, rate limiters, and metadata. `FSWritableFile` tracks preallocation blocks, IO priority, write hint, and strict `bytes_per_sync` behavior. Persistence semantics match `Env`: `Flush` makes data readable and independent of process memory, `Sync` persists data, `Fsync` persists metadata if implemented, directory fsync persists namespace changes, and `Close` surfaces final errors.

## Dependencies and integration points

The header depends on `env.h`, `io_status.h`, `options.h`, `table.h`, `thread_status.h`, `Customizable`, and C++ standard concurrency/utility types. It integrates with `DBOptions::env` through `NewCompositeEnv`, table building and reading, checksum handoff, remote filesystem optimizations, IO tracing, rate limiting, temperature-aware storage, direct IO, async reads, and custom object loading with `FileSystem::CreateFromString`.

## Risks and test signals

Implementations must respect no-exception contracts, thread-safety of the `FileSystem`, and individual file synchronization rules. Async IO is risky because callbacks, `io_handle`, deleters, `Poll`, and `AbortIO` must have clear ownership and completion semantics. Filesystem-owned read buffers require callers to use `result.data()` rather than assuming `fs_scratch` points to char data. `FileOptions` checksum metadata must distinguish unknown, unavailable, and empty-forbidden internal states. Tests should cover wrapper forwarding, IOOptions propagation, debug context copy/request id behavior, default `MultiRead` and async fallback, buffer ownership deleters, path-level sync with file-open contracts, directory listing races, preallocation, range sync strict mode, temperature reporting, and supported-ops gating.
