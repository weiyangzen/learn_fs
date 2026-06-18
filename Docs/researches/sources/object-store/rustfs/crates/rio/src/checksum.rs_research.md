# sources/object-store/rustfs/crates/rio/src/checksum.rs

Purpose: this file implements S3-compatible checksum type parsing, checksum value validation, serialization/deserialization for object metadata, and CRC combination for multipart/full-object checksums.

Important APIs and types: `ChecksumType` is a bitflag wrapper with base algorithms SHA256, SHA1, CRC32, CRC32C, CRC64NVME plus flags for trailing, multipart, includes-multipart, full-object, invalid, and none. It maps algorithms to S3 header keys, raw byte lengths, merge eligibility, object checksum type strings, header parsing, and hasher construction. `Checksum` stores type, base64 encoded value, raw bytes, and expected part count. It can be created from data or strings, validated, matched against content, serialized to maps or bytes, and combined with `add_part`.

Control flow: `get_content_checksum` first handles `x-amz-trailer`, then direct checksum headers or `x-amz-checksum-algorithm`, rejecting duplicates and invalid full-object combinations. Serialization writes checksum type as varint, raw checksum bytes, optional part count, and optional per-part raw checksums. `read_checksums` and `read_part_checksums` parse that format back into header maps. CRC combination uses GF(2) matrix operations for CRC32, CRC32C, and CRC64NVME.

State and persistence: no global state. Persistent state is the encoded checksum metadata stored on objects and reconstructed into response headers. Byte order matters: raw CRCs are stored big-endian for exported/base64 form.

Dependencies and integration points: integrates HTTP headers, `base64`, `sha1`, `sha2`, `crc-fast`, and `crate::errors::ChecksumMismatch`. It is used by upload validation, metadata persistence, and response header generation.

Risks and test signals: parsing must match AWS S3 behavior around duplicate checksum headers, trailing checksums, and full-object restrictions. Multipart serialization silently returns partial buffers if raw length is invalid, which callers must handle. CRC combination is mathematically sensitive to polynomial reflection and length handling. Tests cover CRC64NVME and CRC32C multipart combination against full-object checksums; broader header parsing cases should also be guarded.
