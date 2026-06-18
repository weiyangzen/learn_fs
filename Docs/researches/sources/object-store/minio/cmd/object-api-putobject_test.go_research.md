# sources/object-store/minio/cmd/object-api-putobject_test.go

## Purpose
This test file validates the lower-level `ObjectLayer.PutObject` behavior across MinIO's single-node and erasure-coded test backends. It focuses on object write correctness, request body integrity, bucket/object validation, degraded disk behavior, stale temporary file cleanup, multipart cleanup, and PUT performance benchmarks.

## Important APIs, types, and functions
- `md5Header` builds object metadata containing an expected ETag.
- `TestObjectAPIPutObjectSingle` delegates to `ExecExtendedObjectLayerTest` so the same `testObjectAPIPutObject` table runs against the supported object layer implementations.
- `testObjectAPIPutObject` is the main table-driven correctness test. It creates buckets, constructs `PutObjReader` instances through `mustGetPutObjReader`, calls `obj.PutObject`, and compares exact expected errors and returned ETags.
- `TestObjectAPIPutObjectDiskNotFound` and `testObjectAPIPutObjectDiskNotFound` exercise erasure writes with disks removed, first below and then beyond write quorum.
- `TestObjectAPIPutObjectStaleFiles` and `TestObjectAPIMultipartPutObjectStaleFiles` verify `.minio.sys/tmp` cleanup after normal and multipart object writes.
- The benchmark functions call shared helpers such as `benchmarkPutObject` and `benchmarkPutObjectParallel` for sizes from very small payloads through 50 MiB and for FS/erasure backends.

## Control flow
The main table creates one valid bucket and one unused bucket, then runs invalid bucket names, invalid object names, missing buckets, bad MD5, bad SHA256, size mismatch, valid small/empty/5 MiB payloads, arbitrary metadata, valid combined checksum cases, invalid checksum cases, directory-marker objects with trailing slash, and an invalid CRC32 metadata case. Each case constructs a `PutObjReader` with declared size and checksum expectations, then calls `obj.PutObject` with `ObjectOptions{UserDefined: inputMeta}`.

The disk-not-found test removes four disks in a 16-disk erasure setup and expects writes to continue, then removes one additional disk and expects `errErasureWriteQuorum`. The stale-file tests write a regular object or complete multipart upload and inspect each disk's `minioMetaTmpBucket`, ignoring `.trash`, to ensure no temporary write artifacts remain.

## State and persistence behavior
The tests mutate real test object layer storage: buckets are created, objects and multipart parts are written, disks may be removed with `os.RemoveAll`, and backend temp directories are inspected directly. The table expects persistence-layer checksum and length validation to be enforced during streaming reads, not merely by handler pre-validation. Cleanup tests specifically protect the invariant that successful object writes do not leave stale files under `.minio.sys/tmp`.

## Dependencies and integration points
The file depends on MinIO's test harness helpers (`ExecExtendedObjectLayerTest`, `ExecObjectLayerDiskAlteredTest`, `ExecObjectLayerStaleFilesTest`, `mustGetPutObjReader`), object layer interfaces, `hash` errors, MinIO internal I/O errors, `humanize` sizing constants, and object metadata conventions such as `etag`. It integrates directly with erasure quorum behavior and multipart upload APIs (`NewMultipartUpload`, `PutObjectPart`, `CompleteMultipartUpload`).

## Risks and edge cases
The tests compare some errors by direct equality and others with `errors.Is`, so wrapped errors in the main PutObject table could cause brittle failures. Temp cleanup checks are storage-layout-aware and could need updates if `.minio.sys/tmp` internals change. The invalid CRC32 case currently expects success, which documents that this lower object-layer path does not reject that metadata shape in the same way the HTTP handler might.

## Test signals
Coverage is strong for object-layer PUT validation, degraded erasure writes, and temporary artifact cleanup. It does not exercise the HTTP `PutObjectHandler` authentication, encryption, object lock, replication, or lifecycle paths; those are handler-level responsibilities in `object-handlers.go`.
