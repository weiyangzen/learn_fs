# sources/object-store/minio/cmd/api-response.go

## Purpose
Defines the XML/JSON response models and builders for S3 bucket, object, version, multipart, copy, delete, POST, success, redirect, and error responses.

## Important APIs, types, and functions
- Response structs include `ListVersionsResponse`, `ListObjectsResponse`, `ListObjectsV2Response`, `ListPartsResponse`, `ListMultipartUploadsResponse`, `ListBucketsResponse`, `Object`, `ObjectVersion`, `Metadata`, and delete/copy/multipart result types.
- Builders include `generateListBucketsResponse`, `generateListVersionsResponse`, `generateListObjectsV1Response`, `generateListObjectsV2Response`, multipart/copy/delete response generators, `cleanReservedKeys`, `getObjectLocation`, and `getURLScheme`.
- Writers include `writeResponse`, success helpers, XML/JSON/string error writers, `headersAlreadyWritten`, and `trackingResponseWriter`.

## Control flow
Listing builders transform object-layer listing structs into AWS-compatible XML models, applying URL encoding, ETag quoting, owner fields, storage-class filtering, optional metadata/tag visibility through `metaCheckFn`, encryption metadata reconstruction, reserved metadata stripping, and continuation marker encoding. `writeResponse` refuses to write if a `trackingResponseWriter` already observed headers, normalizes invalid/zero status codes, applies common headers, content type/length, and writes the body.

## State and persistence behavior
Stateless response assembly. Reads global owner id, TLS/default scheme, site region, deployment id, lifecycle/security metadata, and request logger context. No persistence.

## Dependencies and integration points
Central to S3 handlers registered by `api-router.go`. Integrates with MinIO object metadata types, hash checksums, crypto metadata, request scheme handlers, logger request info, xxml encoders, gzip wrappers, and `api-errors.go`.

## Risks and edge cases
Response compatibility is delicate: ETag quoting, base64 continuation tokens, virtual-host locations, metadata filtering, SSE metadata reconstruction, already-written-header suppression, and nonstandard status codes all affect clients. Metadata exposure is policy-gated and security-sensitive.

## Test signals
`api-response_test.go` covers object locations, scheme selection, tracking writer unwrap/header state, and write suppression after headers are already written.
