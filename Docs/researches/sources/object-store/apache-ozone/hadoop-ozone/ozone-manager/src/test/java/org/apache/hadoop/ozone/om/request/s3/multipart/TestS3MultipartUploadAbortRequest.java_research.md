# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadAbortRequest.java

Purpose: tests default-layout `S3MultipartUploadAbortRequest`, including normal abort, missing multipart upload, orphan multipart-info cleanup, and volume/bucket errors.

Important APIs and types: `S3MultipartUploadAbortRequest`, `S3InitiateMultipartUploadRequest`, `CacheKey`, `CacheValue`, `OMRequestTestUtils`, and metadata manager `getMultipartInfoTable` and `getOpenKeyTable`. Helper hooks (`getKeyName`, `createParentPath`, `getMultipartOpenKey`) are overridden by FSO subclass.

Control flow: the success test creates volume/bucket, optionally creates parent path, initiates an MPU, validates initiate to obtain upload ID, pre-executes abort, validates abort, and asserts both `multipartInfoTable` and open-key table rows are gone. Negative tests build abort requests for non-existent MPU, missing volume, and missing bucket. The orphan test deletes the open-key row via a cache tombstone while keeping multipart info, then aborts.

State and persistence behavior: normal abort removes the logical multipart info row and layout-specific MPU open key. The orphan case confirms abort can succeed with `OmKeyInfo` absent in open-key table, cleaning multipart metadata without requiring the open key. Missing volume/bucket or upload must not create or delete unrelated state.

Dependencies and integration points: relies on initiate request to seed legitimate multipart state. The orphan scenario models interaction with `OpenKeyCleanupService`, which may remove open keys before MPU abort cleanup.

Risks covered: abort failing when open-key state is already gone, leaving dangling multipart rows, confusing missing MPU with missing key, and layout-specific open-key name errors. Default variant has no parent hierarchy.

Test signals: expected statuses are `OK`, `NO_SUCH_MULTIPART_UPLOAD_ERROR`, `VOLUME_NOT_FOUND`, and `BUCKET_NOT_FOUND`; table reads return null after successful or orphan abort.
