# sources/object-store/minio/cmd/post-policy_test.go

## Purpose
This test file validates S3 POST policy upload behavior for SigV2, SigV4, malformed requests, content-length policy enforcement, redirects, and a reserved-bucket exploit regression.

## Important APIs, Types, and Functions
Policy builders create V2/V4 JSON policies with bucket, key, credential, date, metadata, content-encoding, and optional content-length conditions. `TestPostPolicyReservedBucketExploit` ensures browser-style POST requests cannot write into `.minio.sys`. `TestPostPolicyBucketHandler` runs V2 and V4 success/failure cases, malformed body/base64/multipart cases, and content-length range checks. `TestPostPolicyBucketHandlerRedirect` verifies `success_action_redirect` uploads and redirect Location construction. Helper constructors build signed multipart requests.

## Control Flow and State
Tests initialize object-layer config, register only the PostPolicy endpoint, create buckets, send requests through the router, and verify HTTP status plus object metadata or backend absence. Some cases intentionally mutate request bodies or content type.

## Dependencies and Integration Points
The tests exercise request signing helpers, POST policy parsing/checking, API router behavior, object-layer writes, erasure disk reads, and response header construction.

## Risks and Test Signals
This is strong regression coverage for policy bypass and malformed request handling. It does not exhaustively test every policy operator or fan-out path. The reserved bucket test depends on erasure internals and browser-enable behavior to reproduce the exploit conditions.
