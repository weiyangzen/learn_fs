# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/v1/AbstractS3SDKV1Tests.java

## Purpose

`AbstractS3SDKV1Tests` is the common JUnit 5 integration-test base for exercising Apache Ozone's S3 Gateway with the AWS Java SDK v1. Concrete standalone and HA/Ratis test classes inherit it via `OzoneTestBase` and `NonHATests.TestCase`, while this base owns the SDK-specific client setup and the behavior suite.

The class validates S3 API compatibility across bucket lifecycle, object put/get/head/copy, object tags, conditional headers, MD5 digest validation, multipart upload, presigned URLs, quota failures, snapshot reads, and edge cases where objects were created through the native Ozone client rather than S3. It also documents unsupported or partially supported S3 features in the leading comment, including versioning, lifecycle, bucket policies, encryption, event notifications, and several ACL modes.

## Important APIs, Types, and Functions

- `createClient()` obtains the `MiniOzoneCluster` from `OzoneTestBase.cluster()` and creates an AWS SDK v1 `AmazonS3` through `S3ClientFactory.createS3Client()`.
- Bucket APIs under test include `createBucket`, `doesBucketExist`, `doesBucketExistV2`, `listBuckets`, `deleteBucket`, `getBucketAcl`, and `setBucketAcl`.
- Object APIs under test include `putObject`, `getObject`, `getObjectMetadata`, `copyObject`, `deleteObject`, `doesObjectExist`, `setObjectAcl`, `setObjectTagging`, and `getObjectTagging`.
- Multipart APIs under test include `initiateMultipartUpload`, `uploadPart`, `completeMultipartUpload`, `abortMultipartUpload`, `listMultipartUploads`, and `listParts`.
- Presigned URL tests use `GeneratePresignedUrlRequest`, `HttpURLConnection`, and helper utilities from `S3SDKTestUtils` to exercise raw HTTP GET, HEAD, PUT, POST, and DELETE flows.
- Native Ozone integration uses `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `OzoneOutputStream`, `OzoneManagerProtocol`, `OmBucketInfo`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, and `ReplicationConfig`.
- Helper methods `multipartUpload`, `initiateMultipartUpload`, `uploadParts`, `completeMultipartUpload`, and `abortMultipartUpload` encapsulate the low-level MPU sequence and assert intermediate response fields.

## Control Flow

The suite is class-lifecycle based (`@TestInstance(PER_CLASS)`) and initializes one shared `AmazonS3` client before tests run. Tests generally allocate unique bucket and key names through `uniqueObjectName()`, create the required bucket, perform one S3 operation sequence, then assert SDK response fields and server-side error mapping.

The object tests progress from basic put/copy behavior into conditional request coverage. `If-None-Match` and `If-Match` cases assert success, `PreconditionFailed` status `412`, and preservation of the original ETag after failed overwrites. Copy-object tests check source ETag constraints; in SDK v1 failed source-copy preconditions are asserted as a null `CopyObjectResult`, which is an SDK-v1-specific behavior worth preserving in compatibility tests.

Multipart control flow follows the AWS sequence: initiate upload, upload parts, collect `PartETag` values, and complete or abort. Pagination tests create multiple outstanding MPUs, walk `keyMarker` and `uploadIdMarker`, check truncation and next-marker semantics, and verify prefix filtering. Part listing tests upload a fixed-size file, page through `ListParts`, and compare part numbers and ETags.

The nested `PresignedUrlTests` creates a fixed bucket once and then uses generated URLs outside the SDK request path. MPU presigned flow manually builds the complete-MPU XML payload, uploads 5 MB chunks with `RandomAccessFile`/`ByteBuffer`, captures ETags from HTTP headers, and posts completion XML back to the S3 Gateway.

## State and Persistence Behavior

Most state is persisted in the MiniOzoneCluster through real S3 Gateway requests. The suite verifies not just SDK return values but durable object metadata, tags, ETags, object presence/absence, and bucket emptiness. Several tests intentionally cross the S3/Ozone boundary: objects created with `OzoneOutputStream` lack S3 ETags and must still be readable/listable through S3, and Ozone snapshots created by `ObjectStore.createSnapshot` must be exposed through `.snapshot/<snapshot>/<key>` S3 keys.

The empty-object tests assert a storage-allocation invariant: a zero-length S3 object has `dataSize == 0`, no key locations, and does not increase SCM allocated-block metrics. Quota tests mutate the underlying Ozone bucket quota and expect S3 writes to fail with `QuotaExceeded`.

Incomplete multipart uploads are treated as bucket contents for delete-bucket purposes until explicitly aborted. This is an important persistence contract because MPU metadata alone must block bucket deletion with `BucketNotEmpty`.

## Dependencies and Integration Points

The file depends on AWS SDK v1 S3 and TransferManager types, JUnit 5, AssertJ, Commons IO, Hadoop/Ozone mini-cluster test infrastructure, Ozone client APIs, S3 Gateway constants/utilities, and S3 error-table constants. It integrates with the Ozone S3 Gateway through `S3ClientFactory`, and with core Ozone services through `MiniOzoneCluster`, SCM metrics, Ozone Manager protocol calls, and Ozone object-store clients.

Important external compatibility points include AWS SDK v1 request/response object shapes, raw HTTP presigned URL behavior, S3-compatible error codes/status codes, MD5/ETag conventions, tag count headers, and multipart marker ordering.

## Risks and Edge Cases

- Tests assume deterministic ETags for known small payloads and per-part MD5 values; changes to checksum semantics or quoting could break many assertions.
- Some SDK v1 behavior differs from v2, notably failed copy preconditions returning `null` rather than throwing an exception.
- The helper `initiateMultipartUpload` only attaches tags when metadata is non-empty, so adding tag-only MPU coverage would need care.
- Multipart helper digest validation reads from a shared `fileInputStream` while upload requests read from the file path; this relies on matching sequential part order.
- Presigned URL MPU code manually serializes XML and strips ETag quotes, making it sensitive to XML shape, ETag quoting, and signed-header requirements.
- ACL tests contain TODO-disabled assertions for bucket ACL correctness and assert object ACL `NotImplemented`; these are test signals for known incomplete functionality.
- Shared nested presigned bucket names are fixed, so concrete subclasses or parallel test execution must avoid cross-run collisions.

## Test Signals

Strong success signals include exact S3 status/error-code assertions (`NoSuchBucket`, `NoSuchKey`, `BucketNotEmpty`, `BadDigest`, `InvalidDigest`, `PreconditionFailed`, `NoSuchUpload`, `QuotaExceeded`, `NotImplemented`), content round trips, metadata/tag validation, pagination marker checks, raw HTTP response codes for presigned URLs, and native Ozone verification of storage allocation and snapshots. The suite is a broad compatibility guard for AWS SDK v1 clients against Ozone S3 Gateway behavior.
