# Research: sources/storage-engines/rocksdb/include/rocksdb/io_status.h

## Purpose

`io_status.h` defines `IOStatus`, a filesystem-oriented subclass of `Status` used throughout RocksDB's file and environment abstractions. It preserves normal RocksDB status codes and subcodes while adding I/O-specific retryability, data-loss, and scope metadata.

## Important APIs, Types, and Functions

`IOStatus` aliases `Status::Code` and `Status::SubCode`, defines `IOErrorScope` values for filesystem, file, and range scope, and provides setters/getters for `retryable_`, `data_loss_`, and `scope_`. Static constructors mirror `Status` families: `OK`, `NotSupported`, `NotFound`, `Corruption`, `InvalidArgument`, `IOError`, `Busy`, `TimedOut`, `NoSpace`, `PathNotFound`, `IOFenced`, and `Aborted`. Copy/move constructors and assignments preserve metadata and state. `status_to_io_status(Status&&)` moves a generic `Status` into an `IOStatus`.

## Control Flow

Most use is value construction and propagation. Filesystem code returns an `IOStatus` directly, often using platform helpers to translate errno or Windows errors into `NoSpace`, `PathNotFound`, or generic `IOError`. The message constructor allocates a joined `msg[: msg2]` string and stores it in inherited status state. Move assignment resets the source object to OK-like defaults after transferring state.

## State and Persistence Behavior

`IOStatus` only carries in-memory status state. It stores code, subcode, retryable flag, data-loss flag, scope, and an optional heap-allocated message inherited from `Status`. It has no durable persistence behavior, but it crosses many persistence boundaries as the error type for file creation, reads, writes, syncs, manifest updates, WAL handling, backup files, and filesystem wrappers.

## Dependencies and Integration Points

The header depends on `rocksdb/slice.h` and `status.h`. Usage spans `env`, `file`, `port/win`, backup, prefetch, manifest, and table I/O layers. `listener.h` wraps `IOStatus` in `IOErrorInfo` for file-I/O callbacks. `WritableFileWriter` uses `IOStatus` to notify listeners about failed writes, syncs, closes, and related operations.

## Risks and Edge Cases

Equality compares only the status code, not subcode, message, retryable flag, data-loss flag, or scope, so tests that need full equivalence must inspect those fields explicitly. Const methods are thread-safe but mutation requires external synchronization. The message constructor asserts that code is non-OK and subcode is valid; invalid constructor use is caught only in assert-enabled builds. `status_to_io_status` can erase explicit I/O metadata if callers first built only a generic `Status`.

## Test Signals

Signals appear in filesystem and environment tests, especially error translation and sync tests. Broader validation comes from RocksDB file readers/writers returning exact subcodes such as `kNoSpace`, `kPathNotFound`, and `kIOFenced`, listener `OnIOError` callback tests, and `ROCKSDB_ASSERT_STATUS_CHECKED` builds that detect unchecked status paths.
