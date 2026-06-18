# sources/object-store/minio/cmd/signature-v4.go

## Purpose
Implements AWS Signature Version 4 canonicalization and signature verification for Authorization-header requests, presigned query requests, and form POST policies. It is the core verifier that reconstructs canonical requests, derives signing keys, and compares client signatures.

## Important APIs, Types, And Functions
Constants include `signV4Algorithm`, `iso8601Format`, and `yyyymmdd`. `serviceType` selects S3 or STS signing scope. Canonicalization helpers are `getCanonicalHeaders()`, `getSignedHeaders()`, `getCanonicalRequest()`, `getScope()`, and `getStringToSign()`. Cryptographic helpers are `getSigningKey()` and `getSignature()`, both backed by HMAC-SHA256.

`doesPolicySignatureMatch()` dispatches V2 vs V4 POST policy verification. `compareSignatureV4()` compares hex signature strings with constant-time comparison. `doesPolicySignatureV4Match()` parses form credentials, validates the access key, derives the policy signing key, and compares the form policy signature. `doesPresignedSignatureMatch()` parses presign query values, validates credentials and headers, checks metadata headers, enforces future-skew and expiry windows, rebuilds the canonical query string without the signature, verifies payload hash and session token consistency, compares signatures, and records `x-amz-signature-age`. `doesSignatureMatch()` verifies Authorization-header signatures using canonical headers, query string, request path, method, payload hash, and request date.

## Control Flow
Canonical request creation lowercases/sorts headers, encodes paths with S3 path rules, preserves canonical query encoding with `+` converted to `%20`, and joins the canonical request fields with newlines. Verification flows parse signature metadata, validate credentials through `checkKeyValid()`, extract signed headers, compute canonical request and string-to-sign, derive the scoped signing key from secret/date/region/service, then constant-time compare expected and provided signatures.

## State And Persistence
No durable state is written. The verifier reads global site region, active credentials, IAM, root-access settings, token/session claims, global clock helpers, and skew constants. `doesPresignedSignatureMatch()` mutates the request header by setting `x-amz-signature-age` after successful verification.

## Dependencies And Integration Points
Depends on MinIO S3 path encoding, set helpers, internal SHA256, auth credentials, MinIO HTTP constants, parser helpers, IAM validation helpers, metadata-header checks, and V2 policy verification. It integrates with S3 object APIs, STS APIs, POST policy upload handling, and request middleware that supplies payload hashes and parsed forms.

## Risks And Edge Cases
This file is security-critical. Query canonicalization must preserve every non-signature parameter exactly, including response override parameters. Presigned verification intentionally treats empty configured region as permissive. Session-token comparison uses constant-time comparison. Time-window checks depend on `UTCNow()` and `globalMaxSkewTime`; skew changes affect accepted future requests. Canonical header extraction delegates important compatibility behavior to `extractSignedHeaders()`.

## Test Signals
`signature-v4_test.go` covers POST policy signature success/failure and presigned-request failures for missing query params, invalid keys, unsigned host/content headers, expiry, future dates, invalid signatures, empty configured region, extra response parameters, and missing signed payload headers. Parser and utility tests cover lower-level canonicalization inputs.
