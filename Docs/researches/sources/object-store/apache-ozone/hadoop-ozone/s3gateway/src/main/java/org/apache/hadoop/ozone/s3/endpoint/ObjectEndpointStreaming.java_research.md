<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectEndpointStreaming.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectEndpointStreaming.java

## Purpose
Static helper for object and multipart writes that use Ozone datastream output instead of the regular `OzoneOutputStream` path. It supports large non-EC PUTs, copy writes, and MPU part uploads while preserving S3 digest and conditional-write behavior.

## Important APIs, types, and functions
- `put` wraps `putKeyWithStream` and translates selected `OMException` values to S3 errors.
- `putKeyWithStream` opens stream keys, copies bytes through `S3ObjectStreamingWriteGuard`, writes ETag metadata, and installs MD5/SHA-256 validation hooks.
- `copyKeyWithStream` streams source data to destination and computes an MD5 ETag from the `DigestInputStream`.
- `createMultipartKey` writes MPU parts through `createMultipartStreamKey` and returns a quoted ETag response.

## Control flow
The helper opens the appropriate datastream key using `createStreamKey`, `createStreamKeyIfNotExists`, or `rewriteStreamKeyIfMatch` based on parsed write conditions. It then copies exactly the expected length, updates metadata latency, stores the computed ETag, attaches pre-commit validators, closes the stream to commit, and returns byte count plus ETag or a JAX-RS response.

## State and persistence behavior
Persistent effects are stream-created object keys and MPU part metadata in Ozone. Metadata mutations happen through the datastream output's `KeyMetadataAware` map before close-time commit. Failure before commit is recorded by the guard so close cannot silently commit a partial transfer.

## Dependencies and integration points
Depends on `OzoneBucket` datastream APIs, `S3ObjectStreamingWriteGuard`, `MultiDigestInputStream`, `S3Utils.validateSignatureHeader`, `S3GatewayMetrics`, `S3ConditionalRequest.WriteConditions`, and S3 constants for checksum headers.

## Risks and edge cases
The path assumes the caller has already excluded EC writes. Signature validation is split: header presence/shape is checked before copying, but actual SHA-256 comparison is a pre-commit hook. MPU datastream exception mapping only handles no-such-upload and permission-denied specially; other OM exceptions bubble to the caller.

## Test signals
Metric tests cover successful and failed create/copy/MPU writes, while object endpoint tests should detect ETag mismatches, invalid `Content-MD5`, SHA-256 mismatch, no-such-upload, and byte length validation. Datastream-specific risk is best caught by tests that force large payloads above the configured threshold.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectEndpointStreaming.java -->
