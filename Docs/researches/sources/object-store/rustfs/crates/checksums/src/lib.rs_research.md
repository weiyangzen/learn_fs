# sources/object-store/rustfs/crates/checksums/src/lib.rs

## Purpose
`lib.rs` is the main implementation of the `rustfs-checksums` crate. It defines supported checksum algorithm names, algorithm parsing, the core `Checksum` trait, concrete checksum implementations, and public module exports.

## Important APIs, Types, and Functions
Public constants define names for CRC32, CRC32C, CRC64NVME, SHA1, SHA256, and MD5. `ChecksumAlgorithm` is a non-exhaustive enum defaulting to `Crc32`; `Md5` is deprecated. `FromStr` performs case-insensitive parsing and maps `md5` to `Crc32`. `into_impl` returns `Box<dyn http::HttpChecksum>`. `as_str` returns canonical names. The `Checksum` trait requires `update`, consuming `finalize`, and `size`. Private structs `Crc32`, `Crc32c`, `Crc64Nvme`, `Sha1`, `Sha256`, and `Md5` implement the trait.

## Control Flow
Parsing checks known names in sequence and returns an `UnknownChecksumAlgorithmError` if none match. `into_impl` constructs default digest state for the selected algorithm. CRC implementations use `crc_fast::Digest` with ISO-HDLC, iSCSI, and NVMe algorithms and return big-endian checksum bytes. SHA and MD5 implementations delegate to digest crates and copy finalized bytes into `Bytes`.

## State and Persistence Behavior
Each checksum struct owns incremental hasher state and is consumed on finalization. No global state or persistence is used.

## Dependencies and Integration Points
Exports `error` and `http` modules and keeps `base64` internal. Integrates with `bytes::Bytes`, `crc-fast`, `sha1`, `sha2`, `md-5`, and HTTP header helpers. Consumers typically parse a `ChecksumAlgorithm`, call `into_impl`, stream `update` calls, then produce HTTP headers through `HttpChecksum`.

## Risks and Edge Cases
`md5` parsing as CRC32 is a compatibility/security policy that may surprise callers expecting Content-MD5. The deprecated `Md5` enum variant still exists but is never returned by `FromStr`. CRC32C test is disabled on PowerPC/PowerPC64, implying architecture-specific concerns in the dependency. `sha1::Digest::as_slice`/`sha2::Digest::as_slice` may produce deprecation warnings depending on dependency versions. `ChecksumAlgorithm` is non-exhaustive, so downstream exhaustive matches are intentionally discouraged.

## Test Signals
Unit tests verify known digest outputs for `"test data"` across CRC32, CRC32C, CRC64NVME, SHA1, SHA256, and internal MD5, plus unknown algorithm error preservation. HTTP tests verify empty-body digest headers and trailer sizes.
