<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/sequence_file_reader.h -->
# sources/storage-engines/rocksdb/file/sequence_file_reader.h

## Purpose

`sequence_file_reader.h` declares `SequentialFileReader`, the public internal wrapper RocksDB uses instead of calling `FSSequentialFile` directly. The class centralizes direct I/O handling, optional readahead wrapping, rate limiter charging, IO tracing, listener notification, and IO stats for sequential read consumers.

## Important APIs, Types, and Functions

- Constructors accept a unique `FSSequentialFile`, file name, optional `IOTracer`, event listeners, optional `RateLimiter`, and `verify_and_reconstruct_read` flag. One overload also accepts a readahead size and wraps the file.
- `static IOStatus Create(...)` opens through a `FileSystem` and returns a ready reader.
- `IOStatus Read(size_t n, Slice* result, char* scratch, Env::IOPriority)` is the main API, with explicit rate-limiter priority.
- `IOStatus Skip(uint64_t n)` advances the sequential position.
- `FSSequentialFile* file()`, `std::string file_name()`, and `bool use_direct_io()` expose underlying state to callers.
- Private `NotifyOnFileReadFinish()`, `AddFileIOListeners()`, and `ShouldNotifyListeners()` implement event-listener integration.
- Private `NewReadaheadSequentialFile()` produces the internal prefetch adapter.

## Control Flow

The header establishes construction-time filtering of listeners: only listeners returning `ShouldBeNotifiedOnFileIO()` are retained. The `Read()` implementation is responsible for deciding whether buffered or direct I/O rules apply. The class stores the rate limiter and verification flag rather than requiring all callers to thread those settings through every read.

## State and Persistence Behavior

`file_name_` is used for diagnostics and listener events. `file_` owns the underlying sequential file through a tracing-aware pointer. `offset_` tracks the reader's sequential offset and is atomic so multiple readers through the same wrapper can reserve offsets without data races. `listeners_`, `rate_limiter_`, and `verify_and_reconstruct_read_` are configuration state. The class itself has no durable persistence behavior.

## Dependencies and Integration Points

The declaration pulls in `env/file_system_tracer.h`, `rocksdb/env.h`, `rocksdb/file_system.h`, `EventListener`, `FileOperationInfo`, `RateLimiter`, and RocksDB port abstractions. It is used by code that needs an `FSSequentialFile` plus RocksDB instrumentation semantics, including WAL/MANIFEST/table-building readers and tests using custom filesystems.

## Risks and Edge Cases

The API assumes caller-provided `scratch` remains valid and large enough for requested output. The rate limiter priority contract notes that the limiter can be charged for `n` even when EOF returns fewer bytes, so callers wanting exact charge should cap `n` by known file size. Direct I/O correctness depends on callers respecting `use_direct_io()` implications indirectly through this wrapper. Listener callbacks must not throw or block unexpectedly, because they run inline on I/O completion.

## Test Signals

Signals include successful creation failure propagation, listener filtering, direct-I/O reads with aligned buffers, rate-limiter bypass with `Env::IO_TOTAL`, verification flag propagation through `IOOptions`, skip behavior, and readahead constructor behavior when the readahead size is too small to be useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/sequence_file_reader.h -->
