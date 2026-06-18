# sources/object-store/minio/cmd/signature-v4-parser_test.go

## Purpose
Provides table-driven unit coverage for Signature V4 parser behavior in `signature-v4-parser.go`. The tests validate parser error mapping and successful extraction of credential scopes, signatures, signed headers, Authorization headers, and presigned query values.

## Important APIs, Types, And Functions
Helper functions include `generateCredentialStr()`, `joinWithSlash()`, `generateCredentials()`, and `validateCredentialfields()`. Test entry points are `TestParseCredentialHeader`, `TestParseSignature`, `TestParseSignedHeaders`, `TestParseSignV4`, `TestDoesV4PresignParamsExist`, and `TestParsePreSignV4`.

## Control Flow
Each test builds explicit raw strings or `url.Values`, invokes the parser under test, checks the returned `APIErrorCode`, and, on success, validates parsed fields. The presign tests construct query parameters from alternating key/value slices and compare normalized date and duration values rather than direct object identity.

## State And Persistence
The file has no persistent state. It uses `UTCNow()` to generate valid date strings, but all state is local to the test cases.

## Dependencies And Integration Points
Depends on the parser types/functions under test, MinIO error code constants, `UTCNow()`, and Signature V4 format constants. These tests are part of the `cmd` package, so they directly access unexported parser helpers.

## Risks And Edge Cases
The tests intentionally cover malformed fields and compatibility cases, including access keys with `/`, `=`, and spaces. They do not exercise `getReqAccessKeyV4()` fallback behavior or IAM validation directly. Time-sensitive cases use current time, which is safe for format parsing but not a full clock-skew verification test.

## Test Signals
Strong signal for parser branch coverage and error-code stability. Any change to accepted credential grammar, service validation, presign expiry semantics, or Authorization header field ordering should require updates here.
