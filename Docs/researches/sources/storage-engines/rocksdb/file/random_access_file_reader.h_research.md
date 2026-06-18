# sources/storage-engines/rocksdb/file/random_access_file_reader.h

## Purpose

`random_access_file_reader.h` declares the RocksDB wrapper around `FSRandomAccessFile`. The wrapper presents synchronous, batched, prefetch, and asynchronous random-read APIs while centralizing direct-I/O handling, rate limiting, listener notification, IO tracing, and statistics.

## Important APIs, Types, and Functions

- `using AlignedBuf = FSAllocationPtr` names ownership returned for aligned async buffers.
- `AlignedBufferAllocationContext` lets callers provide an `AlignedBuffer` and optional allocator for direct-I/O result storage.
- `Align(...)` and `TryMerge(...)` are helper APIs for `FSReadRequest` intervals.
- `RandomAccessFileReader` constructor accepts an `FSRandomAccessFile`, file name, clock, IO tracer, stats/histogram handles, rate limiter, event listeners, file temperature, and last-level flag.
- `Read(...)` supports scratch or direct-I/O allocation-context result storage.
- `MultiRead(...)` supports ordered batches and direct-I/O shared aligned buffers.
- `Prefetch(...)` forwards to the underlying file.
- `PrepareIOOptions(...)` maps `ReadOptions` to `IOOptions`.
- `ReadAsync(...)` and `ReadAsyncCallback(...)` wrap asynchronous random reads.
- Private `NotifyOnFileReadFinish` and `NotifyOnIOError` adapt read events to `EventListener`.

## Control Flow and State

The header establishes ownership and lifetime contracts. The reader is non-copyable and owns its low-level file through `FSRandomAccessFilePtr`, which also carries tracing context. It stores only borrowed pointers for clock, stats, histograms, and rate limiter. It filters listeners to those interested in file IO. `ReadAsyncInfo` owns callback state and, for direct-I/O unaligned reads, may own an `AlignedBuffer` until the callback completes.

## Dependencies and Integration Points

It depends on file-system tracing, platform helpers, `FileSystem`, listeners, options, rate limiting, and aligned buffers. Table readers and file prefetch code use it instead of raw `FSRandomAccessFile` to preserve RocksDB-level IO accounting and listener behavior.

## Risks and Edge Cases

- The direct-I/O allocation context is non-owning with respect to allocator and buffer lifetime; callers must keep them valid for the duration of read submission and result use.
- Async direct-I/O storage may be referenced by completion callbacks, so caller-provided buffers must outlive async operations.
- `MultiRead` requires increasing non-overlapping requests and a non-null direct-I/O buffer context in direct mode.
- The `file()` accessor exposes a mutable raw pointer, so callers can bypass wrapper policy if misused.

## Test Signals

The companion test file validates public helpers and direct-I/O behavior. Prefetch tests exercise the async and prefetch-facing APIs.
