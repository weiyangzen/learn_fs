## sources/object-store/garage/src/api/common/signature/checksum.rs

Purpose: implements Content-MD5 and AWS `x-amz-checksum-*` parsing, calculation, verification, and response header emission.

Important APIs/types/functions: checksum header constants; `ExpectedChecksums`, `Checksummer`, `Checksums`; CRC constructors; `Checksummer::{init, add_md5, add_expected, add_algorithm, update, finalize}`; `Checksums::{verify, extract}`; `parse_checksum_algorithm`; request extraction helpers; `add_checksum_response_headers`.

Control flow: expected checksums initialize only needed digest calculators. Body bytes feed active calculators. Final verification compares base64 MD5, raw sha256 hash, and exactly one extra checksum value. Request parsing accepts one concrete `x-amz-checksum-*` header or a trailer algorithm declared via `x-amz-trailer`.

State/persistence: per-request digest state only. Re-exports model `ChecksumAlgorithm` and `ChecksumValue`, which may be stored with object metadata elsewhere.

Dependencies/integration: used by signature body parsing, S3 put/multipart operations, and response generation. Uses `crc-fast`, `md5`, `sha1`, `sha2`, and base64.

Risks: multiple checksum headers are rejected. Missing requested calculated checksum returns bad request. Trailer algorithm parsing currently expects exactly one supported trailer header name. Digest endian/base64 choices are externally visible S3 compatibility behavior.

Test signals: no local tests here; expected to be covered through upload/checksum API paths.
