# sources/object-store/minio/cmd/auth-handler_test.go

## Purpose
Unit/integration-style tests for auth classification, supported auth modes, presign detection, request signature validation, and admin authentication.

## Important APIs, types, and functions
- `nullReader` and request factories build signed, presigned, V2, V4, and bad-MD5 requests.
- `TestGetRequestAuthType`, `TestS3SupportedAuthType`, `TestIsRequestPresignedSignatureV2`, and `TestIsRequestPresignedSignatureV4` test lightweight classification.
- `TestIsReqAuthenticated` initializes a filesystem object layer and IAM/config subsystems to test signed request validation.
- `TestCheckAdminRequestAuthType` and `TestValidateAdminSignature` test admin-specific signature rules.

## Control flow
The classification tests build synthetic requests and inspect returned auth types/booleans. The authentication tests create temporary FS-backed object-layer state, initialize config/IAM, install test active credentials, sign requests with helper functions, then compare returned `APIErrorCode` values for unsigned, malformed digest, bad digest, valid signed, V2, presigned, and invalid admin credential cases.

## State and persistence behavior
Tests create and remove a temporary filesystem backend via `prepareFS`, write test config, initialize global subsystems, and mutate `globalActiveCred`. Cleanup removes the temp FS directory.

## Dependencies and integration points
Exercise signing helpers, active credentials, object-layer setup, IAM initialization, hash readers, admin policy action checks, and S3 auth verification.

## Risks and edge cases
These tests depend on global subsystem initialization and can be sensitive to test ordering if globals leak. They do not cover JWT, STS action routing, site-replication token signing, object-lock authorization, bucket-policy anonymous authorization, or middleware skew rejection.

## Test signals
Failures show auth-type classification changes, request checksum/signature validation regressions, or admin auth compatibility changes.
