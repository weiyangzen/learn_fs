# sources/object-store/rustfs/crates/signer/src/request_signature_streaming.rs

## Purpose
Adds headers for SigV4 streaming payload requests and contains helpers for chunk string-to-sign/signature derivation. It prepares requests for AWS chunked upload, including optional trailer metadata.

## Important APIs and Functions
`try_build_chunk_string_to_sign` builds a chunk string-to-sign from request time, region, previous signature, and chunk checksum. `_try_build_chunk_signature` derives the S3 signing key and hashes that string. `try_streaming_sign_v4` is the fallible public API; `streaming_sign_v4` is the legacy wrapper that logs and returns the original request on error.

`streaming_sign_v4_inner` mutates headers: `X-Amz-Content-Sha256` becomes either `STREAMING-AWS4-HMAC-SHA256-PAYLOAD` or `STREAMING-AWS4-HMAC-SHA256-PAYLOAD-TRAILER`; trailers become lower-cased `X-Amz-Trailer` entries; trailer use inserts `Transfer-Encoding: aws-chunked`; session tokens become `X-Amz-Security-Token`; `X-Amz-Date` is formatted from `req_time`; and `x-amz-decoded-content-length` is set to a zero-padded decimal length.

## Control Flow and State
The function consumes and returns an `http::Request<s3s::Body>`. Errors are wrapped in `StreamingSignFailure` to preserve the original request for legacy behavior. No body transformation or actual chunk signing happens here; this file primarily annotates headers.

## Integration Points
Uses `request_signature_v4` signing-key helpers, `rustfs_utils::hash::EMPTY_STRING_SHA256_HASH`, `http::HeaderMap`, `time`, and `s3s::Body`. It is re-exported by `lib.rs`.

## Risks
The main function ignores access key, secret key, and region parameters for header mutation, so callers expecting complete streaming authorization must ensure another layer signs the request. It appends rather than inserts some headers, which may create duplicate values. Date formatting includes subsecond (`YYYY-MM-DDTHH:MM:SS.subsecondZ`), while AWS SigV4 canonical timestamps normally use compact no-subsecond form. There are no tests in this file.

## Test Signals
No local unit tests. Behavior is only indirectly covered if downstream integration tests exercise streaming uploads.
