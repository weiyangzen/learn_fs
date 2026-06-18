<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_format.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_log_format.cc

## Purpose
Implements encoding, decoding, and CRC verification for the blob log header, footer, and record header formats shared by readers and writers.

## Important APIs, Types, and Functions
`BlobLogHeader::EncodeTo` and `DecodeFrom` serialize/parse magic number, version, column-family ID, flags, compression, and expiration range. `BlobLogFooter::EncodeTo` and `DecodeFrom` serialize/parse magic number, blob count, expiration range, and masked CRC. `BlobLogRecord::EncodeHeaderTo`, `DecodeHeaderFrom`, and `CheckBlobCRC` handle per-record key size, value size, expiration, header CRC, blob CRC, key, and value verification.

## Control Flow
Header decode validates exact size, fixed fields, magic number, version, flags/compression bytes, and expiration fields. Footer decode computes a CRC over all footer bytes except the CRC field, then validates magic and stored CRC. Record header decode computes the header CRC over key/value sizes and expiration before reading stored CRCs. Blob CRC verification separately hashes key and value slices.

## State and Persistence Behavior
These methods define persistent on-disk blob log bytes. Encoding clears and reserves destination strings, writes fixed-width little-endian fields, and stores masked CRCs. Decoding mutates struct fields but does not own key/value payload storage beyond slices assigned by callers.

## Dependencies and Integration Points
The implementation uses RocksDB fixed-width coding helpers and CRC32C utilities. It is the compatibility contract for `BlobLogWriter`, `BlobLogSequentialReader`, `BlobFileReader`, blob compaction logic, direct-write files, and tests.

## Risks and Edge Cases
Any layout change is format-breaking unless versioned. Header flags currently only interpret bit 0 for TTL; other bits are ignored. Compression type is decoded as a raw byte without support validation. Record header CRC and blob CRC protect different byte ranges, so callers must pass valid key/value slices before `CheckBlobCRC`.

## Test Signals
Reader tests tamper with header, footer, and blob record slices to assert corruption paths. Writer/reader round trips in tests also validate encoded sizes and offsets.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_format.cc -->
