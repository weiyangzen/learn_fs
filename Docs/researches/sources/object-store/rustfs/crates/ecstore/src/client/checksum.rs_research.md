# sources/object-store/rustfs/crates/ecstore/src/client/checksum.rs

## Purpose
Defines checksum modes and helpers for S3 checksum headers, multipart composite checksums, and automatic checksum metadata injection for PUT/multipart completion.

## Important APIs, types, and functions
`ChecksumMode` is an `EnumSetType` with CRC32, CRC32C, SHA1, SHA256, CRC64NVME, none, and full-object flags. Methods include `key`, `raw_byte_len`, `hasher`, `encode_to_string`, `composite_checksum`, and `full_object_checksum`. `Checksum` stores raw checksum bytes and encodes them. `add_auto_checksum_headers` and `apply_auto_checksum` mutate `PutObjectOptions` metadata.

## Control flow
Mode methods map enum variants to S3 header names, raw byte lengths, and concrete `rustfs_checksums` implementations. Composite checksum sorts parts by part number, decodes each part checksum through `ObjectPart::checksum_raw`, concatenates raw part digests, hashes the concatenation, and stores the resulting digest. Full-object checksum currently delegates to the same composite logic for merge-capable CRC modes.

## State and persistence behavior
No global mutable state is kept beyond lazy enum masks. The functions mutate caller-provided `PutObjectOptions.user_metadata` and part slices. Resulting headers become persisted object metadata when remote PUT/complete calls succeed.

## Dependencies and integration points
It depends on `rustfs_checksums`, S3 checksum header constants, URL-safe base64 helpers, `PutObjectOptions`, and `ObjectPart`. It integrates with multipart upload completion and object PUT paths.

## Risks and edge cases
`full_object_requested` checks the masked base algorithm and currently returns true for CRC64NVME rather than an explicit `ChecksumFullObject` flag combination. Full-object CRC merge is not a true range-length-aware CRC combine; it delegates to composite checksum. Metadata replacement in `apply_auto_checksum` overwrites existing user metadata.

## Test signals
No tests are in this file. Indirect coverage comes from multipart/PUT callers. Direct tests should validate header names, base64 length checks, composite sort order, invalid/missing part checksum errors, and preservation or intentional replacement of metadata.
