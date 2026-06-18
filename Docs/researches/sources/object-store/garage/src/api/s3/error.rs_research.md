# sources/object-store/garage/src/api/s3/error.rs

## Purpose
Defines the S3 API error type, conversions from lower-level errors, AWS error-code mapping, HTTP status mapping, response headers, and XML error body rendering.

## Important APIs, Types, And Functions
`Error` is the crate error enum. It wraps `CommonError` and adds S3-specific cases such as `NoSuchKey`, `NoSuchUpload`, CORS/lifecycle missing config, precondition failures, multipart part errors, malformed XML, invalid ranges, invalid encryption algorithms, and invalid checksums. `aws_code` maps variants to S3 error strings. The `ApiError` implementation provides `http_status_code`, `add_http_headers`, and `http_body`.

## Control Flow
Most handlers return `Result<Response<ResBody>, Error>`. Conversions normalize helper errors to internal errors by default, while `pass_helper_error` is re-exported for callers that want specific helper errors exposed. Signature errors are mapped into S3 errors without losing authorization-header detail. Invalid range errors carry the object length so `add_http_headers` can emit `Content-Range: bytes */len`.

## State And Persistence
No persistence. This file controls externally visible protocol state: status codes, XML body fields, CORS wildcard on error responses, and selected headers.

## Dependencies And Integration Points
Depends on `garage_api_common` common errors, generic server `ApiError`, signature errors, helper error mapping, Hyper status/header types, and S3 XML serialization. Every S3 handler relies on this type for `?` propagation.

## Risks And Test Signals
Risk is protocol compatibility: wrong AWS code/status pairs affect clients and SDK retries. XML serialization failure in an error path falls back to a static internal-error XML body. There are no local tests here; confidence depends on common-error tests and integration behavior. The duplicate comment for lifecycle/CORS missing config is harmless but signals copy-paste maintenance risk.
