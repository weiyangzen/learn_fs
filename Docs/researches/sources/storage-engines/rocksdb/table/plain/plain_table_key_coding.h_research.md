<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_key_coding.h -->
# sources/storage-engines/rocksdb/table/plain/plain_table_key_coding.h

Purpose: Declares plain table low-level helpers for writing encoded keys, reading raw bytes from mmap/non-mmap files, and decoding rows.

Important APIs and types: `PlainTableKeyEncoder` exposes `AppendKey()` and `GetEncodingType()`. `PlainTableFileReader` exposes `Read()`, `ReadNonMmap()`, `ReadVarint32()`, `ReadVarint32NonMmap()`, `status()`, and `file_info()`. `PlainTableKeyDecoder` exposes `NextKey()` and `NextKeyNoValue()` and owns a `PlainTableFileReader`.

Control flow: Builders call `AppendKey()` before writing each value length/value. Readers call `NextKeyNoValue()` for index/key scans and `NextKey()` when the value is needed. `PlainTableFileReader::Read()` dispatches directly to mmap memory or to buffered non-mmap reads.

State and persistence: Encoder state includes effective encoding type, fixed user key length, prefix extractor, index sparseness, per-prefix key count, and previous prefix. File reader state includes file info, two buffers, buffer count, and status. Decoder state includes encoding type, fixed user key length, prefix length, saved user key, reconstructed current key, prefix extractor, and an `in_prefix_` flag.

Dependencies and integration points: Depends on `plain_table_reader.h` for reader file info and encoding types, `Slice`, `IterKey`, `ParsedInternalKey`, and writable file wrapper declarations. It is a shared dependency of plain table builder and reader.

Risks: Callers must respect slice lifetime differences between mmap and non-mmap reads. Offsets and lengths are 32-bit and bounded by plain table data end offset. Prefix decoding assumes sorted row order and a prior saved key for suffix rows. The header exposes several decoder fields publicly, making invariants easier to disturb.

Test signals: API coverage through plain table reader/builder, non-mmap buffer reuse, varint read edge cases, prefix/full-key decoding, no-value scans, and status propagation after file read failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_key_coding.h -->
