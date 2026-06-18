# sources/object-store/minio/cmd/httprange_test.go

## Purpose

`httprange_test.go` validates the supported S3 range grammar and the conversion from parsed range specs to object offsets, lengths, and header strings.

## Important Tests And Control Flow

`TestHTTPRequestRangeSpec` uses a resource size of 10 bytes. Valid cases cover open-ended ranges, closed ranges, single-byte ranges, suffix ranges, and suffix ranges larger than the resource. For each, the test parses the header and checks `GetOffsetLength`. It then verifies unparsable strings such as `bytes=-`, `bytes==1-10`, non-numeric values, signed values, and multi-range input return parse errors rather than `InvalidRange`. Finally it checks syntactically valid but unsatisfiable values such as `bytes=5-3`, `bytes=10-`, `bytes=100-`, and `bytes=-0` are classified as invalid ranges either during parsing or offset computation.

`TestHTTPRequestRangeToHeader` parses valid range strings and checks that `ToHeader` reproduces the same header. It also includes malformed inputs where parsing should fail or `ToHeader` should reject the constructed state.

## State, Dependencies, Integration, Risks, And Signals

The test file depends only on Go's `testing` package and package-local range helpers. Its signal is strong for single-range grammar and EOF clamping but does not cover nil `HTTPRangeSpec`, `String(resourceSize)`, negative resource sizes, or very large offsets that might expose the `int64` to `int` conversion in `ToHeader`. The tests intentionally document that multi-range headers are unsupported even though RFC HTTP range syntax permits them.
