<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_index.h -->
# sources/storage-engines/rocksdb/db/blob/blob_index.h

## Purpose
Defines the encoded pointer format stored in the LSM value for blob-backed entries. `BlobIndex` can represent inlined TTL values, external blob references, or external TTL blob references, and provides encode/decode/debug helpers.

## Important APIs, Types, and Functions
`BlobIndex::Type` has `kInlinedTTL`, `kBlob`, `kBlobTTL`, and `kUnknown`. Accessors expose TTL, inlined value, file number, offset, size, and compression after type checks. `DecodeFrom` parses the one-byte type, optional expiration varint, external reference fields, and one-byte compression. `EncodeTo`, `EncodeInlinedTTL`, `EncodeBlob`, and `EncodeBlobTTL` serialize each format. `DebugString` prints either inlined value or external reference metadata.

## Control Flow
Encoding starts with the type byte, then writes varint metadata and either raw inlined value bytes or file/offset/size/compression fields. Decoding mirrors this layout and rejects unknown types or malformed varints/field tails. For external references, exactly one byte must remain for compression after the three varints.

## State and Persistence Behavior
`BlobIndex` is a lightweight decoded view over an encoded LSM value. Inlined values are stored as a `Slice` into the decoded input, so the source buffer must outlive the object when `value()` is used. The persistent bytes are the encoded value stored under `kTypeBlobIndex` or inside wide-column entity metadata.

## Dependencies and Integration Points
The class depends on RocksDB compression enums, `Slice`, varint coding helpers, compression string utilities, and status reporting. It is consumed by blob readers, compaction garbage accounting, DB get/iterator code, wide-column serialization, and direct-write index resolution.

## Risks and Edge Cases
Accessors rely on assertions for type correctness, so production callers must branch on `IsInlined` and `HasTTL` before use. `DecodeFrom` asserts non-empty input before reading the type byte; callers should not pass empty slices. Compression is stored as a raw byte and is not validated here against supported compression managers. Slice-backed inlined values can dangle if decoded from a temporary string.

## Test Signals
The files in this subset exercise `EncodeBlob`, `EncodeInlinedTTL`, `DecodeFrom`, and external-reference accessors in blob reader and garbage meter tests. Broader DB tests should cover TTL blob index behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_index.h -->
