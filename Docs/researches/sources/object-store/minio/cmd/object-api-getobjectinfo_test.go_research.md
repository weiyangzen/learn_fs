# sources/object-store/minio/cmd/object-api-getobjectinfo_test.go

## Purpose
This file tests `ObjectLayer.GetObjectInfo` for validation, missing resources, and metadata returned for normal objects and explicit directory objects. It uses the common object-layer harness so the contract applies to erasure and single-node style backends.

## Important APIs, types, and functions
`TestGetObjectInfo` delegates to `testGetObjectInfo`. The test creates a bucket, uploads `Asia/asiapics.jpg` and `Asia/empty-dir/`, then exercises `ObjectLayer.GetObjectInfo` with `ObjectOptions{}`. Expected outputs are expressed as `ObjectInfo` values containing `Bucket`, `Name`, `ContentType`, and `IsDir`. Expected failures use typed object errors such as `BucketNameInvalid`, `BucketNotFound`, `ObjectNameInvalid`, and `ObjectNotFound`.

## Control flow
The setup creates a bucket and uploads a non-empty JPEG-like object plus an empty directory marker. A table then covers invalid bucket names, valid but missing buckets, empty object names in an existing bucket, missing object names under an existing bucket, and valid objects. Each case calls `GetObjectInfo`, checks pass/fail expectations, compares error messages for failing cases, and verifies selected `ObjectInfo` fields for passing cases.

## State and persistence behavior
The test depends on persisted bucket metadata and object metadata produced by `PutObject`. It expects MIME/content-type inference or metadata handling to identify `Asia/asiapics.jpg` as `image/jpeg`, while the empty directory marker is reported as `application/octet-stream` and `IsDir: true`.

## Dependencies and integration points
Dependencies include the test harness, `bytes.Buffer`, `mustGetPutObjReader`, `ObjectOptions`, and the object API error types. The test integrates with object name validation, bucket lookup, metadata persistence, and directory marker handling.

## Risks and test signals
The strongest signal is that `GetObjectInfo` must fail early and consistently for invalid buckets/object names, must distinguish missing buckets from missing objects, and must preserve directory-marker status. The test does not verify object size, ETag, version IDs, checksums, encryption metadata, retention/legal hold metadata, or range-related behavior.
