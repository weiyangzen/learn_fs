<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/web/error.rs -->
# sources/object-store/garage/src/web/error.rs

## Purpose
Web endpoint error wrapper that maps Garage S3 API errors and website-specific lookup/bad-request failures to HTTP responses.

## Important APIs, types, and functions
`Error::{ApiError, NotFound, BadRequest}` implements `thiserror::Error`. Generic `From<T>` converts anything accepted by the S3 API error type. Methods are `http_status_code` and `add_headers`.

## Control flow
Request handlers convert lower-level errors into this enum, then `error_to_res` in `web_server.rs` asks for status and headers.

## State and persistence behavior
No state. It shapes HTTP status/header output for web clients.

## Dependencies and integration points
Depends on `garage_api_s3::error::Error`, Hyper headers/status codes, and the common `ApiError` trait.

## Risks and test signals
The broad `From<T>` is convenient but can hide unintended conversions through the S3 API error type. Tests should verify NotFound=404, BadRequest=400, and S3 headers are preserved.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/web/error.rs -->
