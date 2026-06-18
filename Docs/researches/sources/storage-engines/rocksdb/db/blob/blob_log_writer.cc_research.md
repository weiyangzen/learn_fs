<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_writer.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_log_writer.cc

## Purpose
Implements append-only writing of blob log files: header, records, footer, sync/close, checksum handoff, and statistics.

## Important APIs, Types, and Functions
`Sync` prepares IO options, syncs the underlying `WritableFileWriter` with optional fsync, and records sync stats. `WriteHeader` encodes and appends `BlobLogHeader`, optionally flushes, updates offsets, and records bytes. `AddRecord` overloads construct a record header with or without expiration and delegate to `EmitPhysicalRecord`. `EmitPhysicalRecord` appends header, key, value, flushes if configured, returns key/value offsets, and updates `block_offset_`. `AppendFooter` encodes the footer, appends, syncs, closes, and extracts file checksum method/value.

## Control Flow
Writers must start with `WriteHeader`, then append zero or more records, then call `AppendFooter`. Assertions enforce the element order in debug builds. `do_flush_` flushes after header/record appends for readers that need immediate visibility, while durability is provided by `Sync` during explicit syncs or footer append. `AppendFooter` short-circuits if the writer has seen an error.

## State and Persistence Behavior
Persistent bytes are appended in blob log format order. `block_offset_` tracks the current file offset and is used to compute returned key and blob value offsets. Footer append syncs and closes the file, and optional checksum outputs come from `WritableFileWriter`. Statistics record bytes written and synced-file events.

## Dependencies and Integration Points
The writer depends on blob log format, `WritableFileWriter`, RocksDB write/system-clock/statistics APIs, sync points, coding utilities, and stop-watch timing. It is used by blob file creation in tests, flush/blob-file builder paths, and `BlobFilePartitionManager` direct-write files.

## Risks and Edge Cases
Offset outputs are set after appends regardless of later flush/stat status, so callers must only use them when status is OK. In release builds, misuse of method order is not protected by assertions. `AppendFooter` resets `dest_` after close attempts, making the writer single-use after finalization. Seen-error handling returns an IOError without trying to close, which callers must propagate.

## Test Signals
Blob reader tests use this writer to generate valid and malformed files. Direct-write tests should verify flush-each-record visibility, sync behavior, footer checksum handoff, and returned offsets.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_writer.cc -->
