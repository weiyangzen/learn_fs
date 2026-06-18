# sources/object-store/minio/cmd/signature-v4-utils.go

## Purpose
Holds shared helper logic for Signature V4 verification: payload hash selection, region comparison, credential lookup, HMAC derivation support, signed-header extraction, whitespace normalization, and metadata-header signing checks.

## Important APIs, Types, And Functions
Constants `unsignedPayload` and `unsignedPayloadTrailer` encode S3 compatibility values for `x-amz-content-sha256`. `skipContentSha256Cksum()` decides whether request-body SHA256 validation can be skipped. `getContentSha256Cksum()` returns the canonical payload hash source, reading and restoring STS bodies when needed. `isValidRegion()` compares request and configured regions while translating legacy `US` to the default MinIO region.

`checkKeyValid()` resolves an access key against root credentials or `globalIAMSys`, handles uninitialized IAM, disabled credentials, token claims, root-access disablement, service-account owner semantics, and session-policy demotion. `sumHMAC()` is the low-level HMAC-SHA256 primitive used by signing-key code. `extractSignedHeaders()` collects all signed header/query values and reconstructs Go-stripped special headers such as `host`, `expect`, `transfer-encoding`, and `content-length`. `signV4TrimAll()` normalizes AWS canonical header whitespace. `checkMetaHeaders()` enforces that all `X-Amz-Meta-*` request headers are represented in the signed header map.

## Control Flow
Payload hash logic branches on presigned vs header-based Signature V4 and on STS service type. Credential validation first checks root credentials, then IAM storage, then session-token claims, then owner/root-access policy. Signed-header extraction requires `host`, resolves normal headers, query parameters, and compatibility special cases, returning `ErrUnsignedHeaders` for missing signed headers.

## State And Persistence
The helper functions mostly compute transient values, but `checkKeyValid()` reads global server state: `globalActiveCred`, `globalIAMSys`, `globalAPIConfig`, token claims, and root-access policy. `getContentSha256Cksum()` temporarily consumes and replaces `r.Body` for STS requests. No persistent writes occur.

## Dependencies And Integration Points
Depends on internal auth, hash, HTTP constants, logger, IAM subsystem globals, policy session claims, and request-classification helpers such as `isRequestPresignedSignatureV4()`. It is used by the parser and verifier files to build canonical requests and authorize request credentials before signature comparison.

## Risks And Edge Cases
Security-sensitive decisions include allowing `UNSIGNED-PAYLOAD`, compatibility skipping of broken empty-SHA256 clients when strict S3 compatibility is disabled, and reconstructing headers removed by Go's HTTP server. `checkMetaHeaders()` compares only the first header value for each metadata header, which matches much S3 metadata usage but can be brittle for multi-valued metadata. IAM initialization errors intentionally map to retryable-style API errors.

## Test Signals
`signature-v4-utils_test.go` covers owner vs IAM user credential validation, checksum-skip rules, region aliases, special signed-header extraction, whitespace trimming including Unicode input, canonical content SHA selection, and metadata-header signing checks.
