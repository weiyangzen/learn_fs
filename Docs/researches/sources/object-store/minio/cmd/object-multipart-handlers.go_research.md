# sources/object-store/minio/cmd/object-multipart-handlers.go

## Purpose
This file implements MinIO's S3 multipart object HTTP handlers: initiate multipart upload, upload a part, copy a part from an existing object, complete an upload, abort an upload, and list uploaded parts. It is the HTTP adaptation layer between S3 request semantics and the `ObjectLayer` multipart API, including auth, encryption, compression, checksums, object lock, replication, quota, versioning, lifecycle tiering, eventing, and XML responses.

## Important APIs, Types, and Functions
- `NewMultipartUploadHandler` validates authorization and request metadata, applies bucket/default encryption, object lock, tags, storage class, replication metadata, compression metadata, checksum preferences, and calls `ObjectLayer.NewMultipartUpload`.
- `CopyObjectPartHandler` parses `X-Amz-Copy-Source`, version ID, range headers, source/destination encryption options, remote-copy needs, compression and encryption transforms, then calls `ObjectLayer.CopyObjectPart`.
- `PutObjectPartHandler` validates part ID, content length, auth/signature type, checksums, quota, multipart metadata, compression/encryption transforms, and calls `ObjectLayer.PutObjectPart`.
- `CompleteMultipartUploadHandler` decodes completion XML, validates sorted parts and object lock headers, computes multipart ETag metadata, enforces preconditions, calls `ObjectLayer.CompleteMultipartUpload`, then sets headers, schedules replication/events/lifecycle cleanup, and writes XML.
- `AbortMultipartUploadHandler` authorizes abort and calls `ObjectLayer.AbortMultipartUpload`, treating `InvalidUploadID` as non-fatal in this implementation path.
- `ListObjectPartsHandler` validates list markers, calls `ObjectLayer.ListObjectParts`, adjusts encrypted/compressed part sizes and ETags, and writes the XML listing.

## Control Flow
All handlers follow the same outer pattern: create context and audit log, extract mux variables, get `ObjectAPI`, authorize with the appropriate policy action, parse query/header inputs, translate them into `ObjectOptions`, call the object layer, map errors with `toAPIError`, and emit S3 XML or header-only responses.

Initiation is metadata-heavy and establishes persistent multipart state. Put-part and copy-part are stream-heavy: they authenticate, enforce size/part limits, build hash readers, optionally compress, optionally encrypt using a part key derived from object key plus part number, attach compression index callbacks, and write part state. Completion is the commit point: it validates completion XML, records the computed multipart ETag in metadata, commits parts to an object version, emits object-created events, schedules replication, updates replica stats, and handles lifecycle transition cleanup. Abort deletes upload state. List reads upload state and normalizes returned part metadata for S3 clients.

## State and Persistence Behavior
Multipart state is persisted through the object layer: initiate creates an upload ID and metadata, put/copy part persists individual parts, complete atomically creates the final object/version and removes or supersedes upload state, abort removes upload state, and list reads current upload state. Metadata persisted or updated includes encryption metadata, compressed-object markers and indexes, object tags, object lock retention/legal hold, replication timestamps/statuses, checksum algorithm/type, storage class, preserved ETags, and versioning/tiering information.

## Dependencies and Integration Points
The file depends on MinIO's auth and policy systems, mux routing, object-layer interfaces, crypto/SSE helpers, hash/checksum package, compression readers, SIO encryption, bucket encryption/object lock/replication/versioning systems, DNS federation for remote copy, MinIO Go client for remote part upload, lifecycle/tier manager, event notifier, audit logger, XML encoders, and HTTP header constants. It is heavily tested by `object-handlers_test.go` and lower-level object API tests.

## Risks and Edge Cases
- Multipart handlers combine many global subsystems; changes in encryption, compression, replication, object lock, versioning, or lifecycle can subtly alter metadata or response headers.
- Streaming and compressed uploads can have unknown encoded sizes, so checksum validation and hash-reader setup must stay aligned with actual/plain sizes.
- SSE-C/SSE-S3/SSE-KMS compatibility paths are strict; wrong headers can expose invalid decryption behavior or incorrect ETags.
- `CompleteMultipartUploadHandler` writes success before sending events and lifecycle cleanup; failures after response are operational side effects rather than API failures.
- Copy-part has remote-copy, range, version, precondition, compression, and encryption branches that are easy to regress without integration coverage.
- Ignored `io.Copy`-style stream errors are limited here because handlers generally pass readers into object-layer APIs, but response writing still assumes encoder success.

## Test Signals
Coverage comes mainly from `object-handlers_test.go`: initiate success/auth/parallel behavior, put-part signed and streaming faults, copy-part source/range/version cases, complete XML/part-order/ETag/size/upload-ID cases, abort behavior, list parts with V2/V4/presigned auth, encryption and compression matrices, anonymous policy behavior, and nil object-layer behavior. `object_api_suite_test.go` adds direct object-layer multipart creation/abort/complete persistence checks.
