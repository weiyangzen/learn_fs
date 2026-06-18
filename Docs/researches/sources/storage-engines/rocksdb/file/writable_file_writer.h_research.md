<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/writable_file_writer.h -->
# sources/storage-engines/rocksdb/file/writable_file_writer.h

## Purpose

`writable_file_writer.h` declares `WritableFileWriter`, RocksDB's internal write-path abstraction over `FSWritableFile`. The class gives higher layers one API for buffered/direct writes, rate limiting, flushing, syncing, file checksums, data verification, listener notifications, and error-state management.

## Important APIs, Types, and Functions

- The constructor wraps a unique `FSWritableFile`, applies `FileOptions`, attaches tracing, stats, listeners, checksum generator factory, verification flags, and optional initial file size.
- `static Create()` opens a new writable file through `FileSystem`.
- `static PrepareIOOptions()` converts public `WriteOptions` into lower-level `IOOptions`.
- Public operations: `Append`, `Pad`, `Flush`, `Close`, `Sync`, `SyncWithoutFlush`, `InvalidateCache`.
- Query/accessors: `file_name`, `GetFileSize`, `GetFlushedSize`, `writable_file`, `use_direct_io`, `BufferIsEmpty`, `IsClosed`, `GetFileChecksum`, `GetFileChecksumFuncName`, `seen_error`.
- Test/error hooks: `TEST_SetFileChecksumGenerator`, `reset_seen_error`, `set_seen_error`, `GetWriterHasPreviousErrorStatus`, and debug-only `seen_injected_error`.
- Private write engines and notification helpers cover buffered writes, direct writes, checksum handoff, range sync, sync internals, and IO option finalization.

## Control Flow

The header shows the intended lifecycle: construct/open, call `Append()`/`Pad()` repeatedly, `Flush()` and `Sync()` as durability policy requires, and `Close()` explicitly or via destructor. The destructor attempts `Close()` with an IO activity value adjusted for stress tests. All public write/sync methods consult `seen_error_`, so most failures make the writer fail-closed until a caller deliberately resets the flag.

## State and Persistence Behavior

Important state includes the wrapped file, aligned write buffer, maximum buffer size, logical/flushed sizes, direct-I/O offset, pending sync flag, last range-sync size, rate limiter, stats/histogram settings, event listeners, checksum generator finalization state, data-verification flags, buffered checksum, and temperature. The class tracks durable write progress so callers can reason about logical file length and flushed lower bounds, but the actual persistence is performed by the underlying filesystem object.

## Dependencies and Integration Points

The declaration depends on version edit definitions for file metadata constants, file-system tracing wrappers, thread-status utilities, file checksum APIs, listener APIs, rate limiter APIs, aligned buffers, sync points, and fault-injection filesystem helpers in debug builds. It is a shared low-level component for DB logging, table building, blob writing, manifest writes, and file-system integration tests.

## Risks and Edge Cases

`initial_file_size` allows wrapping reopened append targets; incorrect values would corrupt logical/flushed offset accounting. Direct writes require a nonzero max buffer size, asserted at construction and validated by `Create()`. Event listener notification helpers are private but numerous, so new file operations need matching listener/error notification to preserve observability. `reset_seen_error()` is explicitly for relaxed-consistency callers and can be unsafe if used after ambiguous partial writes.

## Test Signals

Tests should verify lifecycle idempotence around destructor/`Close()`, direct-write constructor validation, append-after-error behavior, checksum generator injection and finalization, sync-without-flush support checks, listener filtering and callbacks, `GetFlushedSize()` agreement with the underlying file, and debug injected-error reporting.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/writable_file_writer.h -->
