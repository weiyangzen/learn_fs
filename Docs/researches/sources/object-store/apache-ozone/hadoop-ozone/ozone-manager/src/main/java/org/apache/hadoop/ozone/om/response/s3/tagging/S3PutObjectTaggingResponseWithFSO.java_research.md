<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3PutObjectTaggingResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3PutObjectTaggingResponseWithFSO.java

Purpose: FSO variant of S3 put-object-tagging response. It persists updated tag state to the file table using FSO object-ID addressing.

Important APIs/types/functions: Extends `S3PutObjectTaggingResponse`. The success constructor adds `volumeId` and `bucketId`; `addToDBBatch` writes via `getOzonePathKey`; `getBucketLayout` returns `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

Control flow and persistence: The request-mutated `OmKeyInfo` is stored under `(volumeId, bucketId, parentObjectID, fileName)` in the file table through `getKeyTable(getBucketLayout())`. Cleanup metadata names `FILE_TABLE`.

Dependencies and integration: Used by S3 tagging APIs on FSO buckets. Depends on `OmKeyInfo` path identity fields and the base class for common constructors and test access.

Risks and test signals: Main risk is addressing the wrong file-table row or dropping unrelated key metadata. Tests should cover nested paths, same file name under different directories, tag replacement, and failure-constructor no-op behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3PutObjectTaggingResponseWithFSO.java -->
