<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectEndpoint.java

## Purpose
Main object-level JAX-RS endpoint for the Ozone S3 gateway. It implements S3-compatible PUT, GET, HEAD, DELETE, copy object, multipart upload initiation, part upload/copy, and multipart completion, while translating Ozone client and OM behavior into S3 response shapes, metrics, and audit events.

## Important APIs, types, and functions
- `ObjectEndpoint extends ObjectOperationHandler` and installs an `AuditingObjectOperationHandler` wrapping a handler chain of object ACL, object tagging, multipart-key, and default object handlers.
- `put`, `get`, `delete`, `initializeMultipartUpload`, and `completeMultipartUpload` are REST entry points; `handlePutRequest`, `handleGetRequest`, and `handleDeleteRequest` are chain delegates.
- `copyObject`, `copy`, `createMultipartKey`, and `openKeyForPut` implement source-copy, datastream fallback, part commits, and conditional create/rewrite.
- `ObjectRequestContext` caches volume/bucket lookup and carries action, timing, and performance strings through the handler chain.

## Control flow
PUT first checks `uploadId` to route to part upload, then `x-amz-copy-source` to route to copy object, then optional FSO directory creation for zero-length keys ending in `/`, and finally normal object creation. Large non-EC writes use `ObjectEndpointStreaming`; smaller or EC writes use `S3ObjectWriteGuard` over `OzoneOutputStream`. GET obtains key metadata, rejects FSO directories as missing when configured, evaluates conditional headers, parses range headers, and returns a streaming entity for full or partial reads. DELETE delegates through the chain and treats missing keys and non-empty directory markers as S3-compatible no-content success. MPU completion converts ordered XML parts to a `LinkedHashMap`, applies write conditions through generation or ETag, and maps OM MPU failures to S3 errors.

## State and persistence behavior
The endpoint persists object bytes, custom metadata, ETags, object tags, multipart upload state, and directory markers through `OzoneBucket` and `ClientProtocol` calls. It records MD5 ETags in key metadata and optionally validates `Content-MD5` and signed SHA-256 just before stream commit. Conditional writes are delegated to Ozone atomic create/rewrite APIs so persistence semantics are enforced server-side.

## Dependencies and integration points
Integrates with `EndpointBase`, Ozone client volume/bucket/key APIs, OM exception result codes, `S3ConditionalRequest`, `RangeHeaderParserUtil`, `S3Utils`, tagging helpers, storage-class/replication config, datastream output, audit logging, and `S3GatewayMetrics`. It also depends on query constants in `S3Consts` and response DTOs for copy and multipart XML.

## Risks and edge cases
Critical risks are incorrect AWS compatibility around conditional headers, ETag quoting, range handling, source/destination bucket-owner verification, copy metadata/tag directives, and FSO directory semantics. Datastream is deliberately disabled for EC writes, so changes to replication detection can change durability or performance. Pre-commit hooks must run before closing the Ozone stream; otherwise bad MD5/SHA-256 or short body writes could commit.

## Test signals
Nearby tests exercise object GET/HEAD/range behavior, object endpoint copy and MPU paths, audit logging, conditional failures, missing bucket/key mappings, and S3 gateway metric deltas. Strong signals are exact status codes, ETag headers, `x-amz-mp-parts-count`, metric increments, and S3 error codes for `NO_SUCH_UPLOAD`, `PRECOND_FAILED`, `INVALID_REQUEST`, and missing keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectEndpoint.java -->
