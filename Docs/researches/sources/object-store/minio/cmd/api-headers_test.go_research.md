# sources/object-store/minio/cmd/api-headers_test.go

## Purpose
Minimal unit test for request-id generation in `api-headers.go`.

## Important APIs, types, and functions
- `TestNewRequestID` calls `mustGetRequestID(UTCNow())`.

## Control flow
The test generates one id, asserts it has length 16, and verifies every rune is an uppercase alphanumeric character in `0-9` or `A-Z`.

## State and persistence behavior
No state is written. The test depends on the current timestamp returned by `UTCNow()` and on `UnixNano` formatting staying within the expected width for present-era timestamps.

## Dependencies and integration points
Guards a low-level value consumed by response headers and audit/request tracking.

## Risks and edge cases
This does not test uniqueness, monotonicity, request-header propagation, or behavior for arbitrary historical/future times. Because the id is hex, the alphanumeric assertion is broader than necessary but still catches punctuation/lowercase changes.

## Test signals
Failure means request-id formatting changed in a way that could affect client-visible headers or log correlation.
