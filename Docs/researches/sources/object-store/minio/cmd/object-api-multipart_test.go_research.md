# sources/object-store/minio/cmd/object-api-multipart_test.go

## Purpose
This file is the main multipart object API test suite for creating uploads, aborting uploads, uploading parts, listing multipart uploads, listing parts under normal and degraded storage conditions, completing uploads, and benchmarking part uploads.

## Important APIs, types, and functions
Entry points include `TestObjectNewMultipartUpload`, `TestObjectAbortMultipartUpload`, `TestObjectAPIIsUploadIDExists`, `TestObjectAPIPutObjectPart`, `TestListMultipartUploads`, `TestListObjectPartsStale`, `TestListObjectPartsDiskNotFound`, `TestListObjectParts`, `TestObjectCompleteMultipartUpload`, and benchmark functions for FS and erasure part sizes. Object-layer APIs exercised are `MakeBucket`, `DeleteBucket`, `NewMultipartUpload`, `AbortMultipartUpload`, `PutObjectPart`, `ListMultipartUploads`, `ListObjectParts`, and `CompleteMultipartUpload`.

## Control flow
The new-upload and abort tests validate invalid buckets, missing buckets, successful upload initialization, invalid upload IDs, and abort behavior. The put-part test sets up valid and invalid uploads, then checks invalid bucket/object names, missing buckets, mismatched bucket/object/upload ID combinations, MD5 mismatch, SHA256 mismatch, reader overread/underread behavior, and successful part ETag responses.

`testListMultipartUploads` creates multiple buckets with one upload, multiple upload IDs for the same object, and uploads for multiple object names. It uploads parts, then verifies listing by prefix, key marker, upload ID marker, delimiter, max uploads, truncation, next key marker, and next upload ID marker. `testListObjectParts`, `testListObjectPartsStale`, and `testListObjectPartsDiskNotFound` verify part listing fields and pagination. The stale test deletes a part from quorum-majority disks and expects that part to disappear from listings; the disk-not-found test wraps a random disk as faulty and expects degraded listing to remain correct. `testObjectCompleteMultipartUpload` verifies invalid part metadata, ETag mismatch, part-too-small checks, valid completion ETag calculation, and cleanup of the upload ID after successful completion.

## State and persistence behavior
The suite creates real multipart metadata, part objects, and final completed objects in the test backend. It inspects behavior after state mutations such as deleting a bucket used by an upload, aborting an upload, forcing stale part data on erasure disks, injecting faulty disk behavior, and completing an upload. Successful completion must consume multipart state so later operations on the same upload ID fail.

## Dependencies and integration points
Dependencies include the extended object-layer harness, disk-altered harness, erasure server pool internals, storage class parity configuration, naughty disk wrappers, MinIO hash and ioutil errors, `go-humanize` sizes, and multipart MD5 helpers. The tests integrate multipart state with validation, checksum verification, erasure quorum behavior, listing pagination, and final object assembly.

## Risks and test signals
This file catches many high-risk multipart regressions: accepting invalid upload IDs, losing checksum validation, mishandling short/long readers, incorrect multipart listing markers, stale part visibility after disk divergence, degraded-read failures, allowing too-small completed parts, wrong final multipart ETag, and failure to clean temporary multipart state. Some assertions compare error strings while others compare types, so changes to error rendering can break tests even if behavior is otherwise equivalent. Gaps include encrypted multipart paths, checksum algorithms beyond MD5/SHA256 cases shown here, object lock interactions, and replication-specific multipart behavior.
