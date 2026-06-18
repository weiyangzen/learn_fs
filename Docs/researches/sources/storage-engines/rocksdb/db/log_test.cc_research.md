<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_test.cc -->
# sources/storage-engines/rocksdb/db/log_test.cc

## Purpose
Provides the main unit-test suite for RocksDB log reader/writer format behavior. It validates standard and recyclable WAL framing, error handling, EOF retry semantics, user-defined timestamp-size side records, compression metadata, streaming compression round trips, and reader/writer interoperability.

## Important APIs, Types, And Functions
`LogTest` is parameterized by recyclable-log flag, retry-after-EOF flag, and compression type. Its in-memory `StringSource` simulates sequential reads, forced EOF, and forced read errors, while `test::StringSink` captures writer output. Helpers include `Write()`, `Read()`, `IncrementByte()`, `SetByte()`, `ShrinkSize()`, `FixChecksum()`, `ForceError()`, `ForceEOF()`, `UnmarkEOF()`, `MatchError()`, and `CheckRecordAndTimestampSize()`.

`RetriableLogTest` writes real filesystem fragments and uses sync points to coordinate a writer and `FragmentBufferedReader` around partial headers and full headers. `CompressionLogTest` derives from `LogTest` and explicitly writes a compression-type side record before normal records. `StreamingCompressionTest` directly exercises `StreamingCompress`/`StreamingUncompress`.

## Control Flow
The basic tests write records through `log::Writer`, reset the source slice, then read with either `Reader` or `FragmentBufferedReader`. Corruption tests mutate serialized bytes after writing, often fixing CRCs when they want the reader to reach a specific record-type path. Tail tests shrink buffers or force EOF/errors to check tolerant versus absolute recovery behavior. Recycle tests overwrite old in-memory content with a recyclable writer and ensure old records with the wrong log number do not replay. Compression tests initialize writer compression, then validate that the reader sees original uncompressed records.

## State And Persistence Behavior
Most tests use memory-backed file abstractions, but `RetriableLogTest` uses a temporary filesystem path to validate concurrent tailing behavior with `WritableFileWriter::Sync()`. The suite inspects persisted byte counts, block alignment, injected byte corruption, timestamp-size map accumulation, dropped byte accounting, and reported corruption strings. It intentionally simulates stale bytes from recycled logs and partial writes at the end of a file.

## Dependencies And Integration Points
Depends on `db/log_reader.h`, `db/log_writer.h`, `file/sequence_file_reader.h`, `file/writable_file_writer.h`, `test_util/testharness.h`, `test_util/testutil.h`, CRC/coding utilities, random data generation, sync points, filesystem abstractions, and memory allocator utilities. It is the direct regression surface for `log_reader.cc` and `log_writer.cc`.

## Risks And Edge Cases
The tests encode expectations for nuanced behavior: safe-ignorable unknown record types should not report drops; truncated tails may or may not report depending on recovery mode; recyclable logs suppress certain corruption paths by treating stale/corrupt data as EOF; fragment-buffered reads should not flag partial records as corrupt while retry is allowed; and timestamp metadata must be accumulated but not include zero-size entries.

## Test Signals
Named tests include `ReadWrite`, `ReadWriteWithTimestampSize`, `ManyBlocks`, `Fragmentation`, trailer boundary tests, `RandomRead`, all major reader error paths, `ClearEof*`, `Recycle*`, `TimestampSizeRecordPadding`, `TailLog_PartialHeader`, `TailLog_FullHeader`, `NonBlockingReadFullRecord`, compression read/write/fragmentation/checksum tests, and `StreamingCompressionTest.Basic`. Instantiations cover regular and recyclable logs, retry and non-retry readers, no compression, and ZSTD when supported.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_test.cc -->
