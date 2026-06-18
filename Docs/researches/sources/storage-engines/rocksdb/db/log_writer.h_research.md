<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_writer.h -->
# sources/storage-engines/rocksdb/db/log_writer.h

## Purpose
Declares the append-only `log::Writer` interface and documents the RocksDB log file layout. The header is the format contract for legacy and recyclable physical records, block trailer padding, record fragmentation, and public writer operations.

## Important APIs, Types, And Functions
`Writer` is non-copyable and owns a `std::unique_ptr<WritableFileWriter>`. Its constructor accepts log number, recyclable-log mode, manual-flush mode, compression type, WAL verification mode, and an optional initial block offset for appending to an existing log. Public methods include `AddRecord()`, `AddCompressionTypeRecord()`, `MaybeAddPredecessorWALInfo()`, `MaybeAddUserDefinedTimestampSizeRecord()`, `file()`, `get_log_number()`, `WriteBuffer()`, `Close()`, `PublishIfClosed()`, `BufferIsEmpty()`, `TEST_block_offset()`, and `GetLastSeqnoRecorded()`.

Private members define persistent format state: `block_offset_`, `log_number_`, `recycle_log_files_`, `header_size_`, precomputed `type_crc_`, optional streaming compressor, compressed output buffer, recorded timestamp sizes, WAL-tracking flag, and `last_seqno_recorded_`. Private helpers are `EmitPhysicalRecord()`, `MaybeHandleSeenFileWriterError()`, and `MaybeSwitchToNewBlock()`.

## Control Flow
The header's format comment describes fixed `kBlockSize` blocks containing variable-size physical records plus zero padding when a record cannot fit. Legacy headers contain CRC, payload size, and type. Recyclable headers add a 32-bit log number to distinguish current data from bytes left by a previous use of the same file. Logical records larger than the remaining block capacity are split into first/middle/last fragments.

## State And Persistence Behavior
`Writer` manages append state for one log stream. It can be used in manual flush mode where callers control buffer flushing, or default mode where records/side records are flushed after writing. `GetLastSeqnoRecorded()` provides metadata for WAL predecessor verification. Timestamp-size side-record state is monotonic per column family within a writer.

## Dependencies And Integration Points
Includes `db/dbformat.h`, `db/log_format.h`, RocksDB compression/env/IO/status/slice types, hash containers, and `WritableFileWriter`. It is the producer-side counterpart to `log_reader.h` and is directly tested by `log_test.cc`.

## Risks And Edge Cases
Callers must emit compression metadata before compressed data, use `initial_block_offset` correctly when appending to an existing file, and avoid using a writer after `Close()` or successful `PublishIfClosed()`. Manual flushing changes durability timing. Format changes in this header have broad compatibility impact because old WALs and manifests may need to remain readable.

## Test Signals
The header API is covered through `LogTest`, `CompressionLogTest`, and `RetriableLogTest`. `TEST_block_offset()` is used to validate timestamp-size side-record padding behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_writer.h -->
