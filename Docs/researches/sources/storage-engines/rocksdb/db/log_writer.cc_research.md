<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_writer.cc -->
# sources/storage-engines/rocksdb/db/log_writer.cc

## Purpose
Implements RocksDB's append-only log writer for the block-based log format consumed by `log_reader.cc`. It fragments logical records across fixed-size blocks, emits legacy or recyclable physical headers, writes side records for compression, predecessor WAL verification, and user-defined timestamp sizes, optionally compresses WAL payloads, and tracks the largest sequence number written.

## Important APIs, Types, And Functions
`Writer::AddRecord()` is the primary record-writing path. It fragments the input slice, handles block trailer padding, drives optional `StreamingCompress`, chooses full/first/middle/last record types, emits physical records, flushes unless `manual_flush_` is set, and updates `last_seqno_recorded_`. `EmitPhysicalRecord()` formats headers, encodes recyclable log numbers when needed, computes masked CRCs over type/header extension/payload, and appends header and payload to `WritableFileWriter`.

`AddCompressionTypeRecord()` writes the leading compression-type side record and initializes streaming compression buffers. `MaybeAddPredecessorWALInfo()` writes a side record for WAL continuity verification when tracking is enabled. `MaybeAddUserDefinedTimestampSizeRecord()` records new nonzero column-family timestamp sizes and writes a side record before subsequent data. `MaybeSwitchToNewBlock()` pads to the next block when a side record will not fit contiguously. `WriteBuffer()`, `Close()`, `PublishIfClosed()`, `BufferIsEmpty()`, and `MaybeHandleSeenFileWriterError()` manage writer/file state.

## Control Flow
Construction precomputes per-record-type CRC seeds and selects legacy versus recyclable header size. `AddRecord()` first checks for prior file-writer errors, prepares IO options, then loops until all uncompressed or compressed bytes are emitted. If the current block cannot fit a header, it pads the trailer with zeros and resets `block_offset_`. For compressed WALs, compression can produce one or more output chunks; each chunk is further split into physical records as necessary. After successful emission, the writer flushes unless configured for manual flush and records the max provided sequence number.

## State And Persistence Behavior
The writer persists log-format bytes to `WritableFileWriter`. Persistent state includes physical record headers, payloads, CRCs, recyclable log-number fields, compression-type side records, predecessor WAL info records, timestamp-size side records, and zero trailer padding. In-memory state includes current block offset, recorded timestamp-size map, compression stream and buffer, manual-flush mode, log number, recyclable mode, and last sequence number recorded. The destructor attempts a best-effort buffer flush if the destination is still open.

## Dependencies And Integration Points
Depends on `WritableFileWriter`, `db/log_format.h`, `db/dbformat.h`, RocksDB IO/status/slice/write options, compression utilities, UDT utilities, `crc32c`, `coding`, and thread-status helpers. It is used by WAL and manifest/log creation paths and must stay byte-format compatible with `Reader::ReadPhysicalRecord()`.

## Risks And Edge Cases
Block-boundary accounting is critical: the writer must never leave fewer than header-size bytes without padding, and side records must not straddle blocks. Compression initialization must happen after the compression-type record is durably emitted; on failure compression is disabled. Timestamp-size records update in-memory state before writing, so failed side-record writes need careful caller handling. `PublishIfClosed()` assumes `dest_` is non-null; callers using `file()` directly must follow the expected close/publish sequence. Recyclable headers only store low 32 bits of the log number, relying on practical collision improbability plus CRC.

## Test Signals
`log_test.cc` validates round trips, many-block writes, empty records, fragmentation, trailer padding, recyclable overwrite behavior, timestamp-size padding, compression side records and compressed payloads, checksum mismatch handling, and sequence of EOF retry cases. Sync point `LogWriter::EmitPhysicalRecord:BeforeEncodeChecksum` supports corruption-injection testing.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_writer.cc -->
