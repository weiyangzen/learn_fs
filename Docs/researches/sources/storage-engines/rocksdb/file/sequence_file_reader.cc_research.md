<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/sequence_file_reader.cc -->
# sources/storage-engines/rocksdb/file/sequence_file_reader.cc

## Purpose

`sequence_file_reader.cc` implements `SequentialFileReader`, RocksDB's production wrapper around `FSSequentialFile`. It normalizes sequential reads across buffered I/O, direct I/O, optional read-ahead, rate limiting, IO stats, IO tracing, data verification/reconstruction flags, and file-I/O event listeners. The file is on the ingestion/recovery/read side of the storage stack where readers consume WALs, MANIFESTs, table-building inputs, or other sequential files through a consistent API.

## Important APIs, Types, and Functions

- `SequentialFileReader::Create()` opens an `FSSequentialFile` through `FileSystem::NewSequentialFile` and wraps it with a reader carrying a rate limiter.
- `SequentialFileReader::Read(size_t, Slice*, char*, Env::IOPriority)` is the main read path. It builds `IOOptions`, applies `verify_and_reconstruct_read_`, handles direct-vs-buffered I/O, charges the rate limiter, updates `IOSTATS_ADD(bytes_read, ...)`, and notifies listeners.
- `SequentialFileReader::Skip(uint64_t)` advances the tracked direct-I/O offset locally or delegates to `FSSequentialFile::Skip` for buffered files.
- `SequentialFileReader::NewReadaheadSequentialFile()` conditionally wraps the underlying sequential file in an internal `ReadaheadSequentialFile`.
- The anonymous `ReadaheadSequentialFile` class maintains an aligned prefetch buffer, a `buffer_offset_`, and a logical `read_offset_` protected by a mutex.

## Control Flow

`Create()` is straightforward: ask the filesystem for a sequential file, then build a `SequentialFileReader` when that succeeds. `Read()` first sets `rate_limiter_priority` and `verify_and_reconstruct_read` in `IOOptions`. In direct-I/O mode it atomically reserves the logical range by `offset_.fetch_add(n)`, rounds the physical read range to file-buffer alignment, allocates an `AlignedBuffer`, and repeatedly issues `PositionedRead()` calls until the aligned range is filled, an error occurs, or EOF/short read is reached. It copies only the requested unaligned subrange into caller scratch before returning.

In buffered mode `Read()` perturbs `scratch[0]` for paranoia when possible, then loops on `file_->Read()` until `n` bytes, EOF, or error. Listener offsets are based on `offset_.fetch_add(tmp.size())`, so notifications reflect bytes actually returned. Rate limiting can split both buffered and direct reads into smaller underlying file operations unless `Env::IO_TOTAL` bypasses the limiter.

`ReadaheadSequentialFile::Read()` first attempts to satisfy the request from the prefetch buffer. If a complete hit occurs, or the prefetch buffer had reached EOF, it returns immediately. For large reads that would consume almost the full prefetch window, it reads directly from the underlying file and clears the cache. Otherwise it fills the cache with `readahead_size_` bytes and then copies the requested bytes out. `Skip()` consumes cached bytes first, delegates any remainder to the underlying file, and clears stale cache state.

## State and Persistence Behavior

The reader does not persist metadata, but it is stateful. `offset_` is the reader-visible sequential offset and is especially important for direct I/O because direct mode uses positional reads rather than advancing the file object. `ReadaheadSequentialFile` keeps its own `read_offset_` and buffer range to avoid extra remote/file-system calls. Neither wrapper owns durable state; all durable effects are limited to the filesystem data being read and any underlying verification/reconstruction side effects requested through `IOOptions`.

## Dependencies and Integration Points

The implementation depends on `FileSystem`, `FSSequentialFile`, `FSSequentialFilePtr` tracing wrappers, `AlignedBuffer`, rate limiter APIs, `IOOptions`, file-operation listeners, sync points, and `IOSTATS`. It integrates with RocksDB callers that need direct-I/O-safe sequential reads and with event listeners observing file reads. The read-ahead wrapper is an internal adapter used by the constructor overload in the header.

## Risks and Edge Cases

The direct-I/O path is sensitive to alignment math: the physical read range can be larger than the logical request, and only the requested subsection can be returned. Short reads must not copy beyond valid bytes. The `offset_` update happens before direct reads complete, so concurrent calls receive disjoint logical ranges but errors still advance the offset. Buffered listener offsets only advance when listeners are present, while the underlying sequential file advances regardless; this is acceptable for notification accounting but makes listener offset maintenance a separate state path. The read-ahead wrapper has EOF-specific behavior when the buffer fills less than `readahead_size_`, and skip-after-cache logic depends on monotonic `read_offset_`.

## Test Signals

Useful signals include direct-I/O sequential read tests with unaligned logical offsets, EOF short reads, rate-limited multi-token reads, read-ahead cache-hit and cache-miss paths, `Skip()` across cached and uncached ranges, listener callback offset/length assertions, and IO-stat byte counts. Sync-point labels and filesystem wrappers can expose race and error behavior around underlying reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/sequence_file_reader.cc -->
