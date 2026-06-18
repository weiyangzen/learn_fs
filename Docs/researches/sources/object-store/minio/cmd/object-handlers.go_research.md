# sources/object-store/minio/cmd/object-handlers.go

## Purpose
This file implements MinIO's HTTP object API handlers for S3 object operations: SelectObjectContent, GET, HEAD, GetObjectAttributes, COPY, PUT, Snowball-style archive extract, DELETE, object legal hold, retention, tagging, and restore of transitioned objects. It is the integration layer between HTTP/auth/policy semantics and persistent object-layer operations.

## Important APIs, types, and functions
- `setHeadGetRespHeaders` maps supported presigned response override query parameters to response headers.
- `SelectObjectContentHandler` evaluates S3 Select requests over object content using ranged read-seek closures.
- `getObjectHandler`, `GetObjectHandler`, `headObjectHandler`, `HeadObjectHandler`, and `getObjectAttributesHandler` serve object bytes, metadata, ranges, part metadata, checksums, and conditional responses.
- `getCpObjMetadataFromHeader`, `CopyObjectHandler`, remote instance transport/client helpers, and federation checks implement local and federated copy behavior.
- `PutObjectHandler` implements normal PUT object upload with auth, signature verification, checksums, quota, compression, encryption, object lock, replication, lifecycle transition, and event handling.
- `PutObjectExtractHandler` ingests a tar stream and writes extracted entries as individual objects.
- `DeleteObjectHandler` deletes objects or creates delete markers, with object lock retention bypass and delete replication decisions.
- `Put/GetObjectLegalHoldHandler` and `Put/GetObjectRetentionHandler` mutate/read object lock metadata through `PutObjectMetadata`.
- `ObjectTagSet`, `objectTagging`, and tagging handlers manage object tag XML and metadata replication.
- `PostRestoreObjectHandler` validates restore XML, updates restore metadata, and starts background restoration from transitioned storage.

## Control flow
All public handlers create request context, defer audit logging, resolve `ObjectLayer`, decode mux bucket/object variables, authenticate/authorize required policy actions, build operation-specific `ObjectOptions`, and translate internal errors to S3 XML or headers-only responses.

GET and HEAD reject invalid SSE request headers, parse ranges and part numbers, install precondition callbacks, authorize using object tags after fetching metadata, optionally proxy missing/read-quorum objects to replication targets, apply lifecycle expiry locally, filter object lock metadata based on permissions, decrypt object info, emit encryption/checksum/parts headers, apply response header overrides, and send events. GET streams `GetObjectReader` to the response and only writes an error if no data has been sent.

COPY parses and validates `x-amz-copy-source`, source/destination permissions, metadata and tag directives, storage class, bucket encryption defaults, source and destination options, preconditions, source reader acquisition, maximum size, quota, optional recompression, source/target encryption conversion or key rotation, checksum inheritance/recalculation, tag and object-lock metadata, replication metadata, remote federation, and finally `ObjectLayer.CopyObject` or minio-go remote `PutObject`.

PUT validates headers, content length, object size, metadata, tags, authorization, streaming signature mode, SHA256 and MD5 expectations, replication permission checks, quota, bucket encryption defaults, compression, server-side checksums, conditional write callbacks, object lock defaults, replication status, encryption, sensitive metadata removal, tier sweeper setup, and `ObjectLayer.PutObject`. It then writes ETag/encryption/version/checksum headers, emits creation and many-version events, schedules replication and lifecycle transition, and sweeps overwritten transitioned objects.

DELETE builds delete options, blocks force delete on object-lock buckets, configures replication and retention-bypass callbacks, calls `ObjectLayer.DeleteObject`, handles not-found as a successful no-op with event emission, writes delete marker/version headers, schedules delete replication, and sweeps transitioned state.

Object lock and tagging handlers mostly read or mutate metadata while preserving S3 authorization, version ID, replication timestamp/status, and event semantics. Restore updates restore metadata via metadata-only self-copy, returns immediately, and performs actual restore or select restore asynchronously.

## State and persistence behavior
This file is heavily stateful through the object layer. PUT, COPY, archive extract, DELETE, legal hold, retention, tagging, and restore metadata paths all mutate object data or object metadata. Metadata keys drive persistent compression state, actual size, encryption state, object lock retention/legal hold, replication status/timestamps, restore status, storage class, and checksums. Object sweepers remove replaced transitioned objects after successful writes/deletes. Restore launches background work with `GlobalContext`, and replication scheduling queues asynchronous object or delete replication.

## Dependencies and integration points
The handlers integrate with mux routing, MinIO auth and policy systems, bucket encryption config, KMS/SSE-C/SSE-S3/SSE-KMS helpers, hash and checksum readers, object lock, lifecycle, replication, DNS federation, minio-go remote clients, S3 Select, tar extraction, tiering/transition, event notification, audit logging, and shared helpers from `object-api-utils.go` and `object-handlers-common.go`.

## Risks and edge cases
Wrapper ordering around hashing, compression, encryption, ETag sealing, and checksum propagation is critical; a misplaced wrapper can validate the wrong byte stream or leak incorrect ETags. Conditional request semantics depend on callbacks being run after object metadata is available but before data is streamed or overwritten. Several paths mutate `ObjectInfo.UserDefined` maps in place, so unintended aliasing can leak source metadata into destination metadata. GET/HEAD proxy fallback must preserve S3 error compatibility for anonymous requests and missing keys. Restore starts goroutines that must avoid writing to the original response after it has returned; select-restore handling is especially delicate. Object lock and replication metadata timestamp comparisons determine whether incoming replica metadata overwrites local state.

## Test signals
Direct tests in this subset cover object-layer PUT behavior and shared utility/precondition behavior, not this whole handler file. Existing signals include path traversal through the HTTP PUT router, conditional precondition tests, compression utility tests, stale temporary file tests, and object-layer quorum tests. Handler-specific areas needing broader tests include encryption plus compression PUT/COPY, metadata-only copy/key rotation, object lock metadata replication, tag proxying, transitioned-object restore, and anonymous error compatibility.
