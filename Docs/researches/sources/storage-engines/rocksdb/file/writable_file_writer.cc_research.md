<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/writable_file_writer.cc -->
# sources/storage-engines/rocksdb/file/writable_file_writer.cc

## Purpose

`writable_file_writer.cc` implements `WritableFileWriter`, RocksDB's central wrapper around `FSWritableFile`. It handles buffered and direct writes, rate limiting, data verification checksum handoff, file checksum generation, flush/sync/range-sync/close semantics, direct-I/O padding/truncation, IO stats, histograms, and listener notifications. It is a critical write-path component for WALs, MANIFESTs, SSTs, blob files, and other durable outputs.

## Important APIs, Types, and Functions

- `Create()` validates direct-write buffer configuration, opens a writable file, and constructs the writer.
- `Append()` buffers or writes input data, updates file checksums, calls `PrepareWrite()`, maintains `filesize_`, and handles verification checksums.
- `Pad()` appends zero bytes through the buffer and checksum path.
- `Flush()` writes buffered data to the underlying file, calls `FSWritableFile::Flush`, and optionally issues `RangeSync()` according to `bytes_per_sync_`.
- `Close()` flushes, truncates/fsyncs direct-I/O files to logical size, closes the file, and finalizes file checksum generation.
- `Sync()` flushes then syncs/fsyncs buffered files when needed; `SyncWithoutFlush()` syncs only already-flushed bytes if the underlying file supports thread-safe sync.
- `WriteBuffered()`, `WriteBufferedWithChecksum()`, `WriteDirect()`, and `WriteDirectWithChecksum()` are the lower-level write engines.
- `RangeSync()`, `SyncInternal()`, `FinalizeIOOptions()`, `DecideRateLimiterPriority()`, and checksum helpers support the main operations.

## Control Flow

`Append()` rejects calls after a previous error, starts timing, finalizes IO priority from operation and file priorities, marks `pending_sync_`, updates the optional file checksum generator, and calls `PrepareWrite()` with the current logical size. It grows the internal buffer up to `writable_file_max_buffer_size` when that avoids a flush. For buffered I/O, it flushes existing data if the incoming data will not fit, then either accumulates data into the buffer or writes a large chunk directly to `WriteBuffered*`. For direct I/O, data always accumulates in `AlignedBuffer` and gets flushed through positional writes. With data verification and caller-provided crc32c, it preserves whole-buffer checksums so the filesystem can verify the exact byte range.

`Flush()` chooses the appropriate write engine based on direct I/O and checksum handoff, then calls the underlying file's `Flush()`. For buffered I/O with `bytes_per_sync_`, it range-syncs older data while deliberately avoiding the most recent 1 MiB and aligning sync ranges to 4 KiB.

`WriteBuffered()` loops under the rate limiter, calls `Append()` on the underlying file, optionally supplies `DataVerificationInfo`, emits listener callbacks, updates `flushed_size_`, and clears the buffer after success. `WriteBufferedWithChecksum()` first waits until the rate limiter has granted the whole buffer so one checksum covers one append. Direct writes pad to alignment, issue `PositionedAppend()` calls, update flushed bytes, then refit the unaligned tail back to the front of the buffer for a later rewrite. `Close()` flushes, truncates direct-I/O files to `filesize_`, fsyncs direct-I/O output after truncation, closes the underlying file, and finalizes the file checksum only on success.

## State and Persistence Behavior

The writer's state tracks logical size (`filesize_`), flushed physical size (`flushed_size_`), next aligned direct-write offset (`next_write_offset_`), buffered bytes, pending sync status, last range-sync offset, previous-error state, optional checksum generator, buffered crc32c checksum, and file temperature. Durable effects are appends, positioned appends, flushes, sync/fsync calls, range syncs, truncation, and close on the filesystem. After an error, `seen_error_` prevents further normal writes because the underlying file may have partially accepted data; callers can explicitly reset the error for relaxed-consistency cases.

## Dependencies and Integration Points

The implementation depends on `FSWritableFile`, `FileOptions`, `IOOptions`, `WriteOptions` conversion, `AlignedBuffer`, `RateLimiter`, `Statistics`, `StopWatch`, histograms, `IOSTATS`, `crc32c`, file checksum generators, `EventListener`, `FileOperationInfo`, thread-status test helpers, and sync points. It is used by RocksDB table builders, WAL/manifest writers, blob writers, and tests/fault-injection filesystems.

## Risks and Edge Cases

Direct I/O is the highest-risk area: writes must be aligned and positional, tails are padded and later rewritten, and `Close()` must truncate to logical size to hide padding. `flushed_size_` can include padded direct-I/O bytes while `filesize_` is logical data size, so callers must use the right metric. On underlying append failure the buffer is cleared to avoid duplicate data in later retries, which sacrifices transparent retry at this layer. Checksum handoff has two modes: per-chunk checksum calculation and whole-buffer checksum reuse; rate-limited writes with whole-buffer checksum intentionally wait for the full buffer. Listener callbacks receive inline statuses and offsets and must tolerate failures. `SyncWithoutFlush()` is only safe when `IsSyncThreadSafe()` is true.

## Test Signals

Signals include buffered append/flush/sync behavior, direct-I/O tail rewrite and close truncation, `bytes_per_sync_` range-sync offsets, file checksum finalization, data verification checksum handoff, prior-error blocking and injected-error messages, listener notification operation types and offsets, rate-limited write chunking, `GetFileSize()` vs `GetFlushedSize()`, and fault-injection tests ensuring no duplicate buffered data after append failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/writable_file_writer.cc -->
