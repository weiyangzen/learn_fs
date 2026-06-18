# sources/object-store/rustfs/crates/checksums/src/http.rs

## Purpose
`http.rs` maps checksum implementations to S3/AWS-style HTTP checksum header names and values. It defines the `HttpChecksum` trait layered on top of the core `Checksum` trait.

## Important APIs, Types, and Functions
Public header constants include `x-amz-checksum-crc32`, `x-amz-checksum-crc32c`, `x-amz-checksum-sha1`, `x-amz-checksum-sha256`, and `x-amz-checksum-crc64nvme`. `MD5_HEADER_NAME` is crate-visible/dead-code allowed and maps to `content-md5`. `CHECKSUM_ALGORITHMS_IN_PRIORITY_ORDER` prefers CRC64NVME, CRC32C, CRC32, SHA1, then SHA256. `HttpChecksum` provides `headers`, `header_name`, `header_value`, and `size`. Implementations bind `Crc32`, `Crc32c`, `Crc64Nvme`, `Sha1`, `Sha256`, and `Md5` to their header names.

## Control Flow
`headers` consumes a boxed checksum, finalizes it through `header_value`, and inserts one header into a new `HeaderMap`. `header_value` finalizes digest bytes and base64-encodes them into a `HeaderValue`, expecting base64 output to always be header-safe. `size` estimates trailer field size as header-name length plus colon plus base64-encoded digest length.

## State and Persistence Behavior
State lives in the consumed checksum object until finalization. Header maps are newly allocated. No persistence.

## Dependencies and Integration Points
Depends on `http::HeaderMap/HeaderValue`, internal `base64`, and algorithm implementations from `lib.rs`. It is the HTTP-facing adapter for generated clients or S3-compatible body checksum/trailer code.

## Risks and Edge Cases
`header_value` consumes the checksum, so callers cannot update after header generation. `size` omits CRLF and optional whitespace; it models `name:value` bytes only. `HeaderValue::from_str(...).expect` is safe for standard base64 but would panic if the encoding implementation changed to emit invalid header bytes. MD5 support is internal/deprecated and public parsing of `md5` currently returns CRC32.

## Test Signals
Tests assert exact trailer sizes and empty-body header values for CRC32, CRC32C, CRC64NVME, SHA1, and SHA256. They verify canonical zero or known digest bytes after base64 encoding.
