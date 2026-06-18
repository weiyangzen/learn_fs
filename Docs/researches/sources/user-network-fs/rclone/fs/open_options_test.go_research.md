# sources/user-network-fs/rclone/fs/open_options_test.go

## Purpose
`open_options_test.go` validates parsing, rendering, normalization, and header extraction for rclone open options.

## Important APIs, types, and functions
Tests cover `ParseRangeOption`, `RangeOption.Decode`, `RangeOption`, `SeekOption`, `HTTPOption`, `HashesOption`, `NullOption`, `MetadataOption`, `FixRangeOption`, `OpenOptionAddHeaders`, `OpenOptionHeaders`, and `OpenOptionAddHTTPHeaders`.

## Control flow
Range parser tests feed valid and invalid `Range` header strings. Decode tests compare offset/limit math. Option tests assert interface compliance, `String`, `Header`, and `Mandatory` values. Fix tests mutate option slices under different object sizes. Header tests collect a mixed option list into string maps and `http.Header`.

## State and persistence behavior
Tests use in-memory option slices and maps. No external state is touched.

## Dependencies and integration points
The suite depends on Go `http.Header`, rclone `hash.Set`, and testify. It protects every backend that translates open options into HTTP headers or range reads.

## Risks and edge cases
The tests capture important boundary behavior: unsupported multiple ranges, whitespace, open-ended and suffix ranges, zero-size replacement with `NullOption`, unknown-size no-op normalization, and canonical capitalization in `http.Header`.

## Test signals
Coverage is strong for all option implementations present in the file. It does not cover `ParseHeaders`, `MustParseHeaders`, `MetadataAsOpenOptions`, or `ChunkOption`, which remain residual gaps.

Source-read signal: reviewed complete local file (290 lines). Functions/methods observed: `TestParseRangeOption`, `TestRangeOptionDecode`, `TestRangeOption`, `TestSeekOption`, `TestHTTPOption`, `TestHashesOption`, `TestNullOption`, `TestMetadataOption`, `TestFixRangeOptions`, `TestOpenOptionAddHeaders`, `TestOpenOptionHeaders`, `TestOpenOptionAddHTTPHeaders`.
