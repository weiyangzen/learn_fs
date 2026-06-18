<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_sequential_reader.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_log_sequential_reader.cc

## Purpose
Implements sequential reading of blob log files through a `RandomAccessFileReader` while maintaining a cursor. It can read file headers, records at different materialization levels, and footers.

## Important APIs, Types, and Functions
The constructor stores the file reader, clock, statistics, and initializes `next_byte_`. `ReadSlice` reads bytes at the current cursor, advances the cursor, records bytes read, and rejects short reads. `ReadHeader` requires the cursor at zero and decodes a `BlobLogHeader`. `ReadRecord` reads a record header, optionally key or key+value payload, returns the value offset, and checks blob CRC when full payload is read. `ReadFooter` reads and decodes the footer.

## Control Flow
`ReadRecord` always reads the 32-byte record header first. For `kReadHeader`, it skips key and value by advancing the cursor. For `kReadHeaderKey`, it materializes the key and skips the value. For `kReadHeaderKeyBlob`, it materializes key and value and validates blob CRC. The optional `blob_offset` is computed after the header as current cursor plus key size.

## State and Persistence Behavior
The reader does not mutate files; its only state is `next_byte_`, temporary buffer slices, and owned buffers attached to `BlobLogRecord`. It records read latency/bytes in statistics and uses raw `IOOptions`.

## Dependencies and Integration Points
It depends on `RandomAccessFileReader`, blob log format, statistics counters, and `StopWatch`. It is a generic blob log scanner for maintenance or recovery-style code, although the implementation notes it appears lightly used.

## Risks and Edge Cases
`ReadSlice` advances `next_byte_` before checking the read status or short read, so callers cannot retry from the same position without resetting. Large key/value sizes come from the record header and are trusted for allocation/skipping after header CRC validation. The TODO notes missing rate limiting. The macro-based header buffer size should remain synchronized with format sizes.

## Test Signals
No dedicated test is in this subset. Indirect format tests cover decode failures; sequential-reader-specific tests should verify cursor advancement, read levels, blob offsets, short-read corruption, and CRC validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_sequential_reader.cc -->
