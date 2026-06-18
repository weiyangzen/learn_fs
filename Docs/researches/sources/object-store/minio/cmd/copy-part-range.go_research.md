# sources/object-store/minio/cmd/copy-part-range.go

## Purpose
`copy-part-range.go` enforces S3 `x-amz-copy-source-range` semantics for multipart UploadPartCopy requests and maps parse/range errors to S3-compatible API responses.

## Important APIs, Types, And Functions
`writeCopyPartErr` translates `errInvalidRange` to `ErrInvalidCopyPartRange`, `errInvalidRangeSource` to `ErrInvalidCopyPartRangeSource`, and unknown errors to `ErrInvalidCopyPartRangeSource` with a custom description. `parseCopyPartRangeSpec` delegates to `parseRequestRangeSpec` but rejects suffix/open-ended/negative ranges. `checkCopyPartRangeWithSize` verifies the parsed range is within the source object size.

## Control Flow
Parsing accepts only explicit `bytes=first-last`; empty range is handled by the shared parser as whole-resource behavior. Size checking is separate so syntactically valid but out-of-resource ranges can produce the source-range error required by S3 compatibility.

## State And Persistence Behavior
No state is persisted. The file only parses request header values and writes HTTP error responses.

## Dependencies And Integration Points
It depends on shared HTTP range parsing, S3 API error code mapping, and copy-object-part handlers that call these helpers before reading source data.

## Risks And Test Signals
Range semantics differ from ordinary HTTP `Range`, so accepting suffix or open-ended forms would violate UploadPartCopy compatibility. `copy-part-range_test.go` covers valid explicit ranges, malformed forms, and out-of-source ranges.
