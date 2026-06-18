# sources/object-store/minio/cmd/api-resources_test.go

## Purpose
Unit tests for S3 query parser helpers in `api-resources.go`.

## Important APIs, types, and functions
- `TestListObjectsV2Resources` validates V2 list parsing, base64 token decoding, defaults, and empty-token rejection.
- `TestListObjectsV1Resources` validates V1 list parsing and default max keys.
- `TestGetObjectsResources` validates multipart object-resource parsing.

## Control flow
Each test defines table cases with `url.Values`, calls the corresponding parser, and compares all returned fields. V2 includes both explicit and default max-key cases plus an error case where a present empty `continuation-token` returns `ErrIncorrectContinuationToken`.

## State and persistence behavior
No persistent state. Tests are deterministic and only inspect returned parser values.

## Dependencies and integration points
Exercise parser behavior used by list-object and multipart handlers. They depend on shared constants such as `SlashSeparator`, `maxObjectList`, and `ErrNone`.

## Risks and edge cases
Tests do not cover malformed numeric values, invalid base64 continuation tokens, versions-list parsing, bucket multipart parsing, negative limits, or multiple query values. They verify the happy paths used most often and one V2 continuation-token edge case.

## Test signals
Failures indicate changed request-query semantics, especially around defaults and continuation token decoding.
