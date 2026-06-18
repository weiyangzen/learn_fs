# sources/storage-engines/rocksdb/db/blob/blob_file_addition.cc

## Purpose
Implements manifest-log encoding, decoding, equality, and debug rendering for blob-file addition records.

## Important APIs and Control Flow
`EncodeTo` writes blob file number, total blob count, total blob bytes, checksum method, checksum value, optional custom fields via sync point, and an end marker. `DecodeFrom` reads the same fields and then loops over custom field tags. Unknown forward-compatible tags are skipped after reading a length-prefixed value; tags with `kForwardIncompatibleMask` set return corruption. `DebugString`, `DebugJSON`, equality operators, stream output, and `JSONWriter` output expose diagnostic forms with checksum value rendered as hex.

## State, Persistence, and Risks
The binary format is persisted in the manifest, so tag values are compatibility-critical. Dependencies include varint/length-prefixed coding, `Slice`, `Status`, `JSONWriter`, and sync points for test injection. Risks include malformed manifests, checksum method/value consistency only asserted by constructor, and forward-incompatible tag handling. Tests cover empty/non-empty records, decode truncation, and custom-field compatibility.
