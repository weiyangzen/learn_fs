# sources/object-store/rustfs/crates/signer/src/request_signature_streaming_unsigned_trailer.rs

## Purpose
Mutates a request for unsigned SigV4-style chunked streaming with trailers. It is used by SigV4 trailer signing flow after the Authorization header is computed.

## Important APIs and Functions
`streaming_unsigned_v4` inserts `Transfer-Encoding: aws-chunked`, conditionally inserts a valid `X-Amz-Security-Token`, and conditionally inserts `X-Amz-Date` formatted from `req_time`. It accepts but does not use `_data_len`.

## Control Flow and State
The function mutates headers in place and returns the request. Invalid session-token or date header values are silently skipped through `if let Ok(...)` guards; it does not expose a fallible API.

## Integration Points
Called from `request_signature_v4::sign_v4_inner` when trailer headers are present. Uses `http`, `time`, and `s3s::Body`.

## Risks
Silent skipping preserves legacy non-panicking behavior but can leave a request missing expected security token/date headers. The timestamp format includes subsecond and punctuation, not the compact SigV4 timestamp. `_data_len` is unused.

## Test Signals
A unit test verifies that an invalid session token is not inserted, `Transfer-Encoding` is still set, and `X-Amz-Date` exists.
