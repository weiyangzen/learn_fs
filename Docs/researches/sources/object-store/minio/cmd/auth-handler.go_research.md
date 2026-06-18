# sources/object-store/minio/cmd/auth-handler.go

## Purpose
Classifies request authentication type, validates S3/Admin signatures and session tokens, checks IAM/bucket-policy authorization, and installs early auth middleware for S3 requests.

## Important APIs, types, and functions
- Request classifiers: `isRequestJWT`, `isRequestSignatureV4`, `isRequestSignatureV2`, presign detectors, post-policy detector, and streaming/trailer V4 detectors.
- `authType` enum and `getRequestAuthType`.
- Admin auth: `validateAdminSignature`, `checkAdminRequestAuth`.
- Token/claims: `getSessionToken`, `getClaimsFromTokenWithSecret`, `checkClaimsFromToken`.
- S3 auth/authorization: `authenticateRequest`, `authorizeRequest`, `checkRequestAuthType*`, `checkRequestAuthTypeCredential`, `isReqAuthenticated`, `isReqAuthenticatedV2`.
- Middleware/helpers: `setAuthMiddleware`, `isPutRetentionAllowed`, `isPutActionAllowed`.

## Control flow
`getRequestAuthType` parses the raw query into `r.Form` and prioritizes V2, presigned V2, streaming V4, signed V4, presigned V4, JWT, post policy, STS action, anonymous, then unknown. `setAuthMiddleware` rejects unsupported auth and enforces date/skew checks for signed requests before handlers run. `authenticateRequest` verifies signatures, extracts credentials, sets request logger info, and parses create-bucket location payloads. `authorizeRequest` applies anonymous bucket policy or authenticated IAM policy checks, with ListBucketVersions fallback to ListBucket and special delete-version deny handling.

## State and persistence behavior
No persistence, but it mutates request state (`r.Form`, `r.Body`) and request logger context. It reads global credentials, IAM/policy systems, site replication signing key, authz plugin, active site region, skew configuration, and HTTP stats counters.

## Dependencies and integration points
Integrates with SigV2/SigV4 signing helpers, IAM policy engine, bucket policy engine, JWT/auth credentials, object-lock retention policy, hash readers for MD5/SHA256 validation, logger/audit, trace context, and S3/Admin handlers.

## Risks and edge cases
Auth ordering is security-critical. Query parsing errors become unknown auth. Temporary/service-account token rules differ, site-replication signing can change token secret selection, and request body is wrapped for checksum validation. Middleware date rejection increments rejection counters and must audit with claims where possible.

## Test signals
`auth-handler_test.go` covers auth-type classification, supported S3 auth types, presign detection, V4 body/MD5 validation, admin auth acceptance/rejection, and admin signature credential cases.
