# sources/storage-engines/rocksdb/file/random_access_file_reader.cc

## Purpose

`random_access_file_reader.cc` implements `RandomAccessFileReader`, RocksDB's instrumentation and policy wrapper around `FSRandomAccessFile`. It handles direct-I/O alignment, rate limiting, multi-read request alignment/merging, async read callbacks, IO statistics, file-temperature accounting, operation histograms, perf context, IO tracing through the wrapped pointer, and listener notifications.

## Important APIs, Types, and Functions

- `GetFileReadHistograms(...)` maps `Env::IOActivity` to detailed histogram buckets when enabled.
- `RecordIOStats(...)` records bytes/read counts for last-level versus non-last-level files and by `Temperature`.
- `RandomAccessFileReader::Create(...)` opens an `FSRandomAccessFile` and wraps it.
- `Read(...)` performs one random read with direct-I/O alignment/copy handling, optional external aligned allocation, rate limiting, stats, and listener notifications.
- `Align(...)` page-aligns a `FSReadRequest`.
- `TryMerge(...)` merges overlapping or adjacent read intervals.
- `MultiRead(...)` handles batches, including direct-I/O alignment and merged filesystem requests.
- `PrepareIOOptions(...)` converts `ReadOptions` to `IOOptions` using the configured clock or default clock.
- `ReadAsync(...)` submits async reads and prepares callback state for unaligned direct I/O.
- `ReadAsyncCallback(...)` maps aligned async results back to user offsets/buffers, records stats, notifies listeners, and frees callback state.

## Control Flow and State

`Read` first perturbs the scratch byte to avoid stale-data false positives, calculates required alignment, and branches on direct I/O with unaligned inputs. In the unaligned direct-I/O branch, it rounds offset/length to alignment, allocates either an internal or caller-provided aligned buffer, reads in rate-limited chunks, optionally notifies listeners per filesystem read, then returns the requested subrange either by pointing into external aligned storage or copying into scratch. In the normal/aligned branch, it loops until requested bytes are read, rate limiting each chunk and preserving mmap result pointers when the filesystem returns memory outside scratch.

`MultiRead` asserts ordered requests, perturbs scratches, and for direct I/O aligns each request, merges overlapping/adjacent aligned intervals, allocates one large aligned buffer, assigns scratch pointers, and calls `file_->MultiRead`. It then maps filesystem results back to original unaligned requests. It charges rate limiter tokens for the total batch up front and records per-request notifications and byte stats.

`ReadAsync` allocates `ReadAsyncInfo`, records start time/listener start, and for unaligned direct I/O creates an aligned request with aligned storage. On submit failure it deletes callback state. `ReadAsyncCallback` reconstructs the user-visible request, copies or transfers buffer ownership as needed, calls the user callback, records async histograms/error tickers, notifies listeners, records IO stats, and deletes the callback info.

Persistent state is not modified. The reader owns a traced `FSRandomAccessFilePtr`, file name, optional clock/stats/histogram/rate limiter, filtered event listeners, file temperature, and last-level flag. Async operations temporarily own callback metadata and possibly aligned buffers until completion.

## Dependencies and Integration Points

The implementation depends on `file_util.h`, RocksDB histograms/statistics, IO stats context, perf-level helpers, table format constants, sync points, random test hooks, and rate limiter implementation. It is used by table readers, file prefetch buffers, checksum verification, and other code paths needing random file reads with RocksDB observability.

## Risks and Edge Cases

- Direct-I/O code assumes power-of-two alignment semantics through bit masks; invalid filesystem alignment values would break checks.
- Unaligned direct reads can allocate larger rounded buffers, so callers must manage memory pressure and external allocation lifetimes.
- Async direct-I/O callback uses caller-owned scratch or aligned buffer contracts; freeing buffers before callback completion is unsafe.
- `MultiRead` requires sorted non-overlapping input; debug asserts catch order but release builds rely on callers.
- Rate limiting in `MultiRead` charges total bytes in bursts before the call; a TODO notes this can cause burstiness for large batches.
- Listener notification status must be permitted unchecked after callbacks; the implementation does so to avoid status-check assertions.
- `Read` returns an empty result on IO error even if partial bytes were read.

## Test Signals

`random_access_file_reader_test.cc` directly covers direct-I/O read copying, external aligned allocation, multiread alignment/merge behavior, `Align`, and `TryMerge`. `prefetch_test.cc` exercises `ReadAsync`, direct reads through `FilePrefetchBuffer`, async fallback, poll error propagation, and stats integration.
