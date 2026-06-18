<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_reader.cc -->
# sources/storage-engines/rocksdb/db/log_reader.cc

## Purpose
Implements RocksDB's physical and logical log reader for WAL and other log-format streams. It reconstructs logical records from fixed-size block fragments, verifies optional CRCs, handles recyclable-log headers, recognizes metadata record types, supports WAL compression, tracks user-defined timestamp sizes, and reports corruption according to recovery mode. It also implements `FragmentBufferedReader`, a retry-friendly reader used when a caller may see partial records at the current end of a growing file.

## Important APIs, Types, And Functions
`Reader::ReadRecord()` is the central logical-record API. It loops over `ReadPhysicalRecord()`, assembles `kFirstType`/`kMiddleType`/`kLastType` fragments into `scratch`, returns `kFullType` payloads directly, and updates `last_record_offset_` and `first_record_read_` only after a complete user record is found. `ReadPhysicalRecord()` parses legacy and recyclable headers, verifies CRCs, filters old recyclable records by `log_number_`, skips mmap zero records, and applies streaming decompression after a `kSetCompressionType` record.

`ReadMore()` fills a block-sized buffer from `SequentialFileReader`; `UnmarkEOF()` and `UnmarkEOFInternal()` realign the file position when tailing a file that has grown since EOF. `MaybeVerifyPredecessorWALInfo()` validates recorded predecessor WAL metadata against observed WAL metadata when `track_and_verify_wals_` is enabled. `UpdateRecordedTimestampSize()` accumulates nonzero timestamp sizes for column families and rejects repeated entries. `FragmentBufferedReader::ReadRecord()`, `TryReadFragment()`, and `TryReadMore()` preserve partial fragments across failed reads so callers can retry after more data arrives.

## Control Flow
The normal reader clears caller scratch, resets stream checksum state, resets the decompressor if active, then repeatedly obtains physical records. Full records return immediately. First/middle/last fragments update the scratch buffer and a streaming XXH3 checksum when requested. Side records are consumed internally: compression records initialize decompression, predecessor records may report WAL holes or mismatches, and timestamp-size records update the per-column-family map. EOF, old recycled records, bad headers, bad lengths, checksum mismatches, and unknown types are translated into either ignored tail conditions, reporter callbacks, or scan continuation depending on `WALRecoveryMode`.

Physical reads operate one block at a time. The parser requires enough bytes for a minimal or recyclable header, validates payload length against the current buffer, checks the embedded log number for recyclable records, optionally validates CRC from header byte 6 through payload, then returns a payload slice or an uncompressed buffer slice. The fragment-buffered reader uses similar parsing but can return "not ready" without declaring corruption when a header/body is incomplete at EOF.

## State And Persistence Behavior
The file does not persist data itself; it interprets bytes from `SequentialFileReader`. It maintains read cursor state (`buffer_`, `end_of_buffer_offset_`, `eof_offset_`), replay-visible state (`last_record_offset_`, `recorded_cf_to_ts_sz_`, compression mode), and recovery safety state (`recycled_`, predecessor WAL verification inputs, read-error and EOF flags). Corruption reports include approximate dropped bytes and sometimes a specific predecessor log number. Old records in recycled logs act like EOF for normal recovery modes, preventing stale bytes from being replayed.

## Dependencies And Integration Points
Depends on `db/log_format.h` record types, `file/sequence_file_reader.h`, `util/coding.h`, `util/crc32c.h`, `util/compression.h`, `util/udt_util.h`, XXH3 hashing, `WALRecoveryMode`, and optional `Logger`. It is paired with `log_writer.cc`; the tests in `log_test.cc` exercise both sides. Higher layers use `LastRecordEnd()`, recorded timestamp sizes, old-log detection, and corruption callbacks during WAL recovery and tailing.

## Risks And Edge Cases
The recovery-mode matrix is subtle: the same truncated tail is ignored for tolerant recovery but reported for absolute consistency and point-in-time recovery. Recyclable logs intentionally turn checksum and stale-log-number issues into EOF-like conditions in some modes. Compression records must be first and unique, while timestamp-size records must never update an existing column family in a file. `UnmarkEOFInternal()` must preserve unread buffered bytes while aligning to the next block. The fragment-buffered reader currently does not support record checksums for logical records, and it has different tail-corruption behavior by design.

## Test Signals
`log_test.cc` covers empty files, normal read/write, fragmentation, trailers, aligned EOF, random reads, read errors, bad record types, safe-ignore types, bad lengths, checksum mismatch, missing fragments, EOF clearing, recycled logs, timestamp-size side records, compression, streaming compression, and retriable partial-header/body reads through `FragmentBufferedReader`. Sync points include `LogReader::ReadMore:AfterReadFile` and `FragmentBufferedLogReader::TryReadMore:FirstEOF`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_reader.cc -->
