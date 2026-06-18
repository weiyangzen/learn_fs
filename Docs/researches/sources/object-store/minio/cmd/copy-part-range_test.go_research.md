# sources/object-store/minio/cmd/copy-part-range_test.go

## Purpose
`copy-part-range_test.go` verifies strict parsing and source-size validation for `x-amz-copy-source-range`.

## Important APIs, Types, And Functions
`TestParseCopyPartRangeSpec` calls `parseCopyPartRangeSpec`, `HTTPRangeSpec.GetOffsetLength`, and `checkCopyPartRangeWithSize`.

## Control Flow
The test first validates successful ranges against a ten-byte object and checks resulting start/end offsets. It then asserts malformed or unsupported range strings fail parsing. Finally, it checks syntactically valid ranges outside object bounds fail size validation with `errInvalidRangeSource`.

## State And Persistence Behavior
No persistent state is used.

## Dependencies And Integration Points
The test depends on shared range parser behavior and the copy-part-specific helpers. It documents MinIO's expected UploadPartCopy range subset.

## Risks And Test Signals
The suite does not test empty range behavior or HTTP response mapping in `writeCopyPartErr`. It is a strong unit signal for the most error-prone grammar differences from normal HTTP range handling.
