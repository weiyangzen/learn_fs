# sources/object-store/minio/cmd/api-resources.go

## Purpose
Parses S3 query parameters for bucket/object list and multipart resource APIs into typed values plus `APIErrorCode` parse results.

## Important APIs, types, and functions
- `getListObjectsV1Args` parses `prefix`, `marker`, `delimiter`, `max-keys`, and `encoding-type`.
- `getListBucketObjectVersionsArgs` parses version-list markers, version marker, delimiter, max keys, and encoding.
- `getListObjectsV2Args` parses V2 list parameters, `fetch-owner`, max keys, and base64 continuation tokens.
- `getBucketMultipartResources` parses bucket-level multipart upload listing parameters.
- `getObjectResources` parses object-level multipart part listing parameters.

## Control flow
Each parser starts with `ErrNone`, reads optional numeric limits with defaults (`maxObjectList`, `maxUploadsList`, `maxPartsList`), and returns specific invalid-argument codes when conversion fails. V2 listing rejects an explicitly present empty continuation token and decodes non-empty continuation tokens from base64 before returning them to callers.

## State and persistence behavior
Stateless pure parsing over `url.Values`; no global state or persistence.

## Dependencies and integration points
Feeds S3 list-object, list-version, list-multipart-upload, and list-parts handlers. Uses constants from `api-response.go` and error codes from `api-errors.go`.

## Risks and edge cases
The functions parse integers but do not enforce semantic bounds beyond parse success; downstream handlers must clamp or validate negative/large values. Empty V2 continuation tokens are rejected only when the key is present. Invalid base64 maps to `ErrIncorrectContinuationToken`.

## Test signals
`api-resources_test.go` covers V1/V2 defaults, valid token decoding, empty token rejection, and object multipart parameter extraction.
