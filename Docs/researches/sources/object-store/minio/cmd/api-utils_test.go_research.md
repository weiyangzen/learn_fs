# sources/object-store/minio/cmd/api-utils_test.go

## Purpose
Unit tests for S3 response-name encoding in `api-utils.go`.

## Important APIs, types, and functions
- `TestS3EncodeName` table-drives inputs through `s3EncodeName`.

## Control flow
Each case supplies input text, encoding type, and expected output. The test verifies no encoding when `encodingType` is empty and S3-specific URL encoding when it is `url`.

## State and persistence behavior
No state is modified.

## Dependencies and integration points
Guards encoding behavior consumed by list-object, list-version, multipart, and common-prefix response generators.

## Risks and edge cases
The test covers representative ASCII characters but not non-ASCII UTF-8, control characters, long strings, or lowercase/mixed-case `encoding-type` values. It also has a duplicate `p/` case, which is harmless but redundant.

## Test signals
Failures indicate changed S3 key/prefix URL encoding, which can break clients relying on `encoding-type=url`.
