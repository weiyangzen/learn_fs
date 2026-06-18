# sources/object-store/minio/cmd/signature-v4-parser.go

## Purpose
Implements parsers for AWS Signature Version 4 credential scopes, Authorization headers, and presigned-query parameters. The file converts raw S3/STS request authentication fields into structured `credentialHeader`, `signValues`, and `preSignValues` records that later verification code can canonicalize and compare.

## Important APIs, Types, And Functions
`credentialHeader` stores the parsed access key plus date, region, service, and `aws4_request` scope fields. Its `getScope()` method rebuilds the canonical credential scope string. `signValues` models an Authorization header with credential, signed headers, and signature. `preSignValues` embeds `signValues` and adds presign request time and expiry duration.

`getReqAccessKeyV4()` extracts credentials from form-style `X-Amz-Credential` first, then falls back to the Authorization header and returns `checkKeyValid()` results. `parseCredentialHeader()` accepts access keys containing `/`, validates key syntax through `auth.IsAccessKeyValid`, parses the date with `yyyymmdd`, validates the configured region via `isValidRegion`, enforces S3 vs STS service names, and requires `aws4_request`. `parseSignature()` and `parseSignedHeader()` validate individual `Signature=` and `SignedHeaders=` tags. `doesV4PresignParamsExist()` checks the required presign query keys. `parsePreSignV4()` validates algorithm, credential, ISO8601 date, non-negative and <= 7-day expiry, signed headers, and signature. `parseSignV4()` normalizes spacing while preserving spaces inside the credential/access key portion.

## Control Flow
Header parsing flows from raw input into tag-level validators, then into credential-scope validation, then into the final structured value. Presigned parsing first performs required-parameter presence checks, then rejects unsupported algorithm values before parsing the credential scope, date, expiry, signed headers, and signature. Authorization parsing strips `AWS4-HMAC-SHA256`, demands exactly three comma-separated fields, and delegates each field to the narrower parser.

## State And Persistence
This file is stateless. It reads `http.Request` headers/forms and global region/service context only through helper calls, and returns `APIErrorCode` values instead of mutating persistent storage.

## Dependencies And Integration Points
Depends on MinIO auth key validation, MinIO HTTP header constants, region/service constants from `signature-v4.go`, and `checkKeyValid()`/`isValidRegion()` from `signature-v4-utils.go`. Its outputs feed `doesSignatureMatch()`, `doesPresignedSignatureMatch()`, POST policy verification, and request access-key discovery for S3 and STS endpoints.

## Risks And Edge Cases
The parser is security-sensitive: permissive space removal, access keys containing separators, and fallback from form credential to Authorization header all affect compatibility and potential ambiguity. Expiry parsing appends `s`, so only second-based presign expiry strings are accepted. Region validation intentionally accepts request region when configured region is empty, which preserves ListBuckets compatibility but broadens accepted credential scopes.

## Test Signals
`signature-v4-parser_test.go` covers malformed credential tags, invalid keys/date/region/service/request version, access keys containing `/`, `=`, and spaces, signature/signed-header parsing, Authorization header parsing, required presign parameters, malformed presigned dates/expiries, negative expiry, and maximum 7-day expiry enforcement.
