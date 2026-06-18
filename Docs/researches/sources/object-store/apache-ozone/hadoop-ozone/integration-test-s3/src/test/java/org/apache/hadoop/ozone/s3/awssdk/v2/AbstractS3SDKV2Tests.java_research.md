# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/v2/AbstractS3SDKV2Tests.java

## Purpose

`AbstractS3SDKV2Tests` is the AWS Java SDK v2 counterpart to the SDK v1 S3 Gateway integration-test base. It verifies Ozone's S3-compatible behavior using v2 `S3Client`, `S3AsyncClient`, v2 presigner APIs, v2 transfer manager, and v2 model exception semantics.

The class overlaps with v1 coverage for core bucket/object/MPU/presigned behavior, but it also adds v2-only or v2-focused compatibility checks: conditional GET/HEAD requests, destination-side copy preconditions, resumable transfer-manager download after ETag mismatch, expected-bucket-owner verification for many endpoints, link-bucket ownership cases, and the S3 Express-style `ListDirectoryBuckets` API over Ozone FSO buckets.

## Important APIs, Types, and Functions

- `createClient()` builds `S3Client` and `S3AsyncClient` via `S3ClientFactory.createS3ClientV2()` and `createS3AsyncClientV2()`.
- `closeClient()` closes both clients after the class, reducing resource leakage from Apache HTTP/async client internals.
- Core SDK v2 APIs under test include `putObject`, `getObject`, `getObjectAsBytes`, `headObject`, `copyObject`, `listBuckets`, `listObjects`, `listObjectsV2`, object tagging APIs, and delete APIs.
- Multipart APIs use `CreateMultipartUploadRequest/Response`, `UploadPartRequest/Response`, `CompletedPart`, `CompletedMultipartUpload`, and `CompleteMultipartUploadRequest/Response`.
- Presigned flows use `S3Presigner` and typed presign requests for get/head/put/delete/create-MPU/upload-part/complete-MPU. The tests execute the URLs with both `HttpURLConnection` and AWS SDK v2 `SdkHttpClient`.
- `S3TransferManager` and `ResumableFileDownload` validate SDK v2 transfer behavior against Ozone object replacement.
- Nested ownership tests exercise `expectedBucketOwner` and `expectedSourceBucketOwner` across bucket, object, tagging, MPU, copy, delete, and link-bucket calls.
- `ListDirectoryBucketsTests` uses `ListDirectoryBucketsRequest`, `ListDirectoryBucketsResponse`, and Ozone `BucketLayout.FILE_SYSTEM_OPTIMIZED` buckets to validate directory-bucket listing behavior.

## Control Flow

The class initializes shared sync and async clients once per class and closes them at the end. Most tests build request objects through SDK v2 builders, perform an operation, and assert v2 response fields or `S3Exception` details.

Core object flow checks ETag quoting as emitted by SDK v2, tag parsing for header-only tag keys, sorted tag-return order, conditional put failure behavior, conditional GET/HEAD response codes (`304` and `412`), zero-byte object storage invariants, and MD5 validation. Multipart tests initiate, upload, complete, or abort using explicit SDK v2 model objects and use `stripQuotes` where server ETags need to be compared to raw MD5 hex.

Copy tests cover both source preconditions (`copySourceIfMatch`, `copySourceIfNoneMatch`) and destination preconditions (`ifMatch`, `ifNoneMatch`). Unlike the v1 suite, failed preconditions are expected to throw `S3Exception` with status `412`.

The nested presigned tests build an SDK v2 `S3Presigner` from the live client's endpoint, region, credentials provider, and path-style configuration. They then execute signed URLs through two independent HTTP paths. The MPU presigned test runs two complete upload cycles, one via `HttpURLConnection` and one via `SdkHttpClient`, each manually uploading parts and posting complete-MPU XML.

Ownership verification first creates a default bucket, records the owner from `getBucketAcl`, and seeds an object. It then verifies correct owner values pass and `WRONG_OWNER` fails with `403 Access Denied` across endpoint groups. Link-bucket tests create source buckets in a non-S3 volume and link them into the S3 volume, including a dangling-link case after deleting the source bucket.

Directory-bucket tests create FSO buckets through the Ozone client, call `listDirectoryBuckets` by setting `maxDirectoryBuckets`, and verify filtering, pagination, response fields, max-zero behavior, and coexistence with regular `ListBuckets`.

## State and Persistence Behavior

The tests persist real buckets, keys, tags, multipart upload state, link-bucket metadata, and snapshots in the MiniOzoneCluster. They inspect persisted object data through SDK reads, Ozone native reads, head responses, tag counts, and storage metrics. Empty-object storage is verified to avoid block allocation just as in the v1 suite.

The resumable download test intentionally persists one object version, pauses a transfer, overwrites the object with different content, and resumes. The expected persistence behavior is that the resumed transfer detects the ETag mismatch and downloads the current object content rather than leaving stale data.

Ownership tests rely on persisted ACL owner metadata and expected-owner checks being enforced before endpoint actions mutate state. Directory-bucket tests persist FSO bucket layout metadata and then clean those buckets through Ozone APIs in `finally` blocks.

## Dependencies and Integration Points

This file integrates AWS SDK v2 S3 sync/async clients, the SDK v2 Apache HTTP client, the SDK v2 presigner, SDK v2 transfer manager, JUnit 5, AssertJ, Commons IO, Ozone MiniOzoneCluster, Ozone object-store APIs, Ozone bucket layout/link-bucket APIs, and S3 Gateway constants/utilities.

It is an important compatibility boundary for SDK v2 model behavior: quoted ETags, typed exceptions, builder-only request construction, expected-owner headers, `ListDirectoryBuckets` routing, presigner signed headers, and transfer-manager resume semantics.

## Risks and Edge Cases

- Many assertions depend on SDK v2 ETag quoting, while helpers sometimes strip quotes; inconsistent server quoting can break otherwise valid data paths.
- Presigned PUT and MPU tests mutate signed header maps before HTTP execution; changes in presigner immutability or required signed headers could affect the tests.
- The `testPresignedUrlDelete` second half reuses a presigned DELETE URL after re-uploading the object, which assumes the URL remains valid for the same bucket/key and duration.
- `initiateMultipartUpload` always builds `Tagging.builder().tagSet(tags)`; callers currently pass tags in the low-level helper path, but a future null call would need guarding.
- Directory-bucket tests create and delete FSO buckets through Ozone native APIs, so cleanup failures can affect later list results.
- Ownership tests share fixed bucket/key names inside nested classes; parallel subclass execution needs isolation.
- Link-bucket and dangling-bucket coverage depends on Ozone ownership resolution semantics, which are more complex than plain bucket ACL reads.

## Test Signals

Key signals are exact `S3Exception` status/error-code assertions, successful content round trips, tag count and sorted tag validation, ETag changes after overwrites, zero-block empty object verification, transfer-manager resumed content validation, expected-owner `403 Access Denied`, link-bucket pass/fail checks, presigned raw HTTP status codes, and directory-bucket filtering/pagination/field assertions. The class is a high-value regression guard for AWS SDK v2 compatibility and newer S3 Gateway features.
