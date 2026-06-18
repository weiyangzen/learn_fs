# sources/object-store/rustfs/crates/checksums/src/base64.rs

## Purpose
`base64.rs` is a small internal wrapper around `base64-simd` standard base64 encoding. It centralizes encoding, decoding, encoded-length calculation, and error presentation for checksum header values.

## Important APIs, Types, and Functions
`DecodeError` wraps `base64_simd::Error`, implements `std::error::Error`, and displays a stable `"failed to decode base64"` message while exposing the source error. `decode` returns decoded bytes from an input string. `encode` returns a standard base64 string for bytes. `encoded_length` returns the encoded length for a byte length.

## Control Flow
All functions delegate directly to `base64_simd::STANDARD`. `decode` maps the external error into `DecodeError`; `encode` and `encoded_length` are infallible wrappers.

## State and Persistence Behavior
No mutable state or persistence. All operations are pure conversions.

## Dependencies and Integration Points
Used by checksum tests and `http::HttpChecksum::header_value`/`size` to encode digest bytes and estimate trailer sizes. It hides the chosen base64 implementation from the rest of the crate.

## Risks and Edge Cases
The module is `pub(crate)` and marked `#![allow(dead_code)]`, so unused functions may remain for tests or future verification paths. Decode error display intentionally omits the detailed source text, which is available only through `source()`.

## Test Signals
No direct tests live in this file, but checksum tests use `base64::decode` to verify hex digest values and HTTP tests use `base64::encode` for expected empty-body digest headers.
