# sources/object-store/minio/cmd/signature-v4_test.go

## Purpose
Provides targeted regression coverage for Signature V4 policy and presigned URL verification paths in `signature-v4.go`.

## Important APIs, Types, And Functions
`niceError()` formats MinIO `APIErrorCode` values for readable assertion output. `TestDoesPolicySignatureMatch()` validates V4 POST policy handling. `TestDoesPresignedSignatureMatch()` validates presigned query verification error ordering and compatibility cases.

## Control Flow
The policy test prepares a temporary filesystem object layer, builds form headers, and asserts missing credential, invalid access key, bad signature, and valid policy outcomes. The presigned test prepares config, computes a fixed payload hash, constructs table-driven query/header maps, creates requests, parses forms, then calls `doesPresignedSignatureMatch()` and checks exact error codes.

## State And Persistence
Tests create temporary object-layer/config state through `prepareFS()` and `newTestConfig()`, then remove the filesystem root. Request state is local to each test case.

## Dependencies And Integration Points
Depends on active global test credentials, MinIO test object-layer setup, Signature V4 constants and signing helpers, `doesPolicySignatureMatch()`, and `doesPresignedSignatureMatch()`. It exercises integration between parser, canonicalizer, credential validation, and request time checks.

## Risks And Edge Cases
The table focuses on expected rejection paths and one valid policy case, but does not include a fully valid presigned request. Some expected errors depend on validation order, so refactors that change order may require careful review even if final rejection remains correct.

## Test Signals
Strong signal for error-code stability in authentication middleware. Covers common failure classes: missing auth fields, invalid credentials, unsigned headers, expired/future presigns, invalid signatures, empty region behavior, and extra non-auth query parameters.
