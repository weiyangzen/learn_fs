# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadCompleteRequest.java

Purpose: tests default-layout `S3MultipartUploadCompleteRequest`, from pre-execution through final key-table materialization, multipart/open cleanup, overwrite accounting, invalid part ordering, and not-found statuses.

Important APIs and types: `S3MultipartUploadCompleteRequest`, `S3MultipartUploadCommitPartRequest`, `S3InitiateMultipartUploadRequest`, `BatchOperation`, `Table`, `CacheKey`, `RepeatedOmKeyInfo`, `OmBucketInfo`, protobuf `Part`, `OzoneConsts.ETAG`, and metadata tables for open keys, multipart info, closed keys, deleted keys, and buckets.

Control flow: success helper initiates MPU with metadata/tags, commits one part, extracts the ETag from commit request metadata, builds a complete request with a matching part, validates, then explicitly calls `omClientResponse.checkAndUpdateDB` in a batch and commits it. The test repeats the whole flow for the same key with different metadata/tags to exercise overwrite. Separate tests submit unordered parts, missing volume, missing bucket, and no-such upload.

State and persistence behavior: successful complete removes the multipart open key and multipart-info row, inserts the completed object into the key table with multipart locations, preserves metadata and tags from initiate, and updates bucket used namespace. On overwrite, the old key is represented in the deleted table; `checkDeleteTableCount` validates deleted-key accounting. The explicit batch commit means this class validates response persistence as well as cache updates.

Dependencies and integration points: commit-part request must produce the ETag consumed by complete. Bucket namespace expectations are layout-dependent through `getNamespaceCount`, overridden by FSO. `getPartName` uses production static part-name construction for invalid-order test setup.

Risks covered: completing with wrong part order, losing metadata/tags, leaving stale multipart/open rows, failing overwrite cleanup, incorrect namespace accounting, and not applying response DB updates. Empty/missing MPU paths must return precise statuses.

Test signals: statuses `OK`, `INVALID_PART_ORDER`, `VOLUME_NOT_FOUND`, `BUCKET_NOT_FOUND`, and `NO_SUCH_MULTIPART_UPLOAD_ERROR`; null open/multipart rows; non-null closed key row marked multipart; deleted-table count after overwrite; bucket used namespace equals expected.
