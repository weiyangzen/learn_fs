# sources/object-store/rustfs/crates/ecstore/src/client/api_error_response.rs

## Purpose
Provides S3-style client error response structures and helpers to convert HTTP responses or local upload validation errors into `ErrorResponse` values.

## Important APIs, Types, and Functions
- `ErrorResponse` stores S3 error code, message, bucket/key/resource, request/host IDs, region, server, and local `StatusCode`.
- Custom serde keeps `RequestId` PascalCase and maps error-code strings to `S3ErrorCode`.
- `to_error_response` extracts an embedded `ErrorResponse` from `std::io::Error`.
- `http_resp_to_error_response` parses XML error bodies or synthesizes errors from HTTP status, then overlays headers such as `Server`, `x-minio-error-code`, `x-minio-error-desc`, `x-amz-request-id`, `x-amz-id-2`, and `x-amz-bucket-region`.
- Constructors include `err_transfer_acceleration_bucket`, `err_entity_too_large`, `err_entity_too_small`, `err_unexpected_eof`, `err_invalid_argument`, and `err_api_not_supported`.

## Control Flow and State Behavior
HTTP conversion first turns the body into lossy UTF-8. If headers are empty or the status is client/server error, the function immediately returns `ResponseInterrupted` with "Invalid HTTP response"; otherwise it tries to parse XML and falls back to status-based S3 codes. Header-derived overrides are applied after parsing/fallback.

## Dependencies and Integration Points
Uses `http`, `serde`, `quick_xml`, `thiserror`, and `s3s::S3ErrorCode`. Most client API modules wrap this response in `std::io::Error::other`.

## Persistence
No persistence. This is wire-error translation.

## Risks and Edge Cases
- The early return on `resp_status.is_client_error()` or server error prevents parsing normal S3 XML error bodies for most error statuses. That likely collapses useful remote errors into `ResponseInterrupted`.
- `serialize_code` serializes every code as an empty string, so JSON serialization loses the actual error code.
- Several messages use curly quotes, which can be awkward for exact S3 compatibility.
- `to_error_response` only extracts when the inner error reference is exactly `ErrorResponse`; string-wrapped errors become default responses.

## Test Signals
One inline test validates that JSON serialization uses `RequestId` and does not expose `request_id`. There are no tests for XML parsing, header overrides, status fallback mapping, or code serialization fidelity.
