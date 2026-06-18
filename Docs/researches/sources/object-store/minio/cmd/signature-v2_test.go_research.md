# sources/object-store/minio/cmd/signature-v2_test.go

Purpose: This file tests Signature V2 canonical resource ordering, presigned URL validation, Authorization header validation, and POST policy signature validation.

Important APIs and types: Tests cover `resourceList`, `doesPresignV2SignatureMatch`, `preSignV2` test helper, `validateV2AuthHeader`, `doesPolicySignatureV2Match`, and `calculateSignatureV2`. Setup uses `prepareFS`, `newTestConfig`, and global active credentials.

Control flow: `TestResourceListSorting` copies and sorts `resourceList` and asserts the original is already sorted. `TestDoesPresignedV2SignatureMatch` initializes test config, builds requests with missing/invalid/expired/bad-signature query parameters, and for success cases signs the request with `preSignV2` before validation. `TestValidateV2AuthHeader` table-tests empty, wrong prefix, missing fields, bad access key, and valid access key headers. `TestDoesPolicySignatureV2Match` table-tests invalid access key, wrong signature, and correct signature for a simple policy string.

State and persistence behavior: The tests create a temporary filesystem object layer and global test config so credential validation works. No durable state beyond temp directories is kept.

Dependencies and integration points: These tests use auth/config setup helpers, URL encoding, global credentials, and S3 API error codes. They isolate Signature V2 logic from full HTTP server tests.

Risks: The presign success cases depend on `preSignV2` helper behavior matching production validation; shared helper bugs could reduce independence. Time-based expiry uses `UTCNow()` and short future offsets, but it is deterministic enough for unit tests. The tests do not exhaustively cover canonicalized x-amz headers or every subresource.

Test signals: Expected error codes include `ErrInvalidQueryParams`, `ErrInvalidAccessKeyID`, `ErrMalformedExpires`, `ErrExpiredPresignRequest`, `ErrSignatureDoesNotMatch`, `ErrAuthHeaderEmpty`, `ErrSignatureVersionNotSupported`, `ErrMissingFields`, and `ErrNone`; the policy test verifies correct HMAC-SHA1/base64 matching.
