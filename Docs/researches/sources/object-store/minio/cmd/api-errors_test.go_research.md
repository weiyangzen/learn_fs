# sources/object-store/minio/cmd/api-errors_test.go

## Purpose
Unit tests for the API error translation registry in `api-errors.go`.

## Important APIs, types, and functions
- `toAPIErrorTests` maps representative Go/internal errors to expected `APIErrorCode` values.
- `TestAPIErrCode` calls `toAPIErrorCode` against each table entry.
- `TestAPIErrCodeDefinition` iterates from `ErrNone + 1` to `apiErrCodeEnd` to validate table completeness.

## Control flow
The translation test runs a simple table loop using `t.Context()`, comparing returned codes with expected codes for hash, object-layer, bucket, multipart, quorum, SSE-C, signature, nil, and unknown errors. The definition test walks the whole enum range and fails immediately if an error code is absent from `errorCodes`, has an empty XML code, or has a zero HTTP status.

## State and persistence behavior
No durable state is modified. The tests enforce `APIErrorCode` enum order and `errorCodes` table completeness as source-level invariants.

## Dependencies and integration points
Depends on `internal/crypto`, `internal/hash`, object-layer error structs from the cmd package, and the generated enum sentinel `apiErrCodeEnd`. It indirectly guards response generation because missing status/code fields would produce invalid API responses.

## Risks and edge cases
Coverage is representative rather than exhaustive for the large table. The completeness test catches missing mappings for new constants but does not validate semantic correctness of every HTTP status/message. Unknown errors are expected to map to `ErrInternalError`.

## Test signals
Failures indicate either a changed error classification, an unmapped new `APIErrorCode`, or an incomplete wire-facing table entry.
