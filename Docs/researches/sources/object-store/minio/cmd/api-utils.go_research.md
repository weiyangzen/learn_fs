# sources/object-store/minio/cmd/api-utils.go

## Purpose
Small S3 API utilities for AWS-compatible URL encoding of response names and for deriving handler names from reflected function values.

## Important APIs, types, and functions
- `shouldEscape` identifies bytes requiring percent-encoding, preserving alphanumerics plus `-`, `_`, `.`, `/`, and `*`.
- `s3URLEncode` encodes names for S3 `encoding-type=url`, using `+` for spaces, uppercase hex, preserving `/` and `*`, and encoding `~`.
- `s3EncodeName` conditionally applies URL encoding when encoding type is `url`.
- `getHandlerName` strips cmd package/type receiver suffixes from reflected handler function names.

## Control flow
`s3URLEncode` first counts spaces and hex escapes to avoid allocation when unnecessary and to use a stack buffer for small outputs. It then either replaces spaces only or emits `%XX` escapes for every byte requiring escaping. `getHandlerName` calls `runtime.FuncForPC` and trims package/type and method-wrapper suffixes.

## State and persistence behavior
Stateless; no global reads except package-name assumptions embedded in string trimming.

## Dependencies and integration points
Used by list-response builders for S3 key/prefix encoding and by `s3APIMiddleware` for API stats/log names. Depends on Go reflection/runtime and MinIO handler naming conventions.

## Risks and edge cases
Encoding is byte-oriented and intentionally differs from `url.QueryEscape` for S3 compatibility. Handler-name extraction is brittle if package paths, receiver types, or compiler wrapper suffixes change.

## Test signals
`api-utils_test.go` checks URL encoding for spaces, percent, slash, tilde, asterisk, plus, underscore, and dot.
