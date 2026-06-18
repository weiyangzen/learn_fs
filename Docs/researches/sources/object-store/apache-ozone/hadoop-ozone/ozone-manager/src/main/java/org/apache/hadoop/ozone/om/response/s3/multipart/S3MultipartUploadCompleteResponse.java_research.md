<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCompleteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCompleteResponse.java

Purpose: Applies the OM metadata changes for successful S3 multipart upload completion in non-FSO layouts. It converts an MPU from open multipart state into a committed key and schedules unused part versions for deletion.

Important APIs/types/functions: Extends `OmKeyResponse`. The success constructor stores `multipartKey`, `multipartOpenKey`, final `OmKeyInfo`, `allKeyInfoToRemove`, `BucketLayout`, optional `OmBucketInfo`, and `bucketId`; the failure constructor calls `checkStatusNotOK()`. `addToDBBatch` is the main API. `addToKeyTable`, `getOmKeyInfo`, `getOmBucketInfo`, and `getMultiPartKey` support subclass specialization.

Control flow and persistence: `addToDBBatch` deletes the multipart open key from the open-key table for the layout, deletes the MPU entry from `MultipartInfoTable`, writes the completed `OmKeyInfo` to the key table, writes unused part `OmKeyInfo` instances to `DeletedTable` under `getOzoneDeletePathKey(objectID, multipartKey)`, and updates `BucketTable` if bucket usage changed.

Dependencies and integration: Used by complete-MPU request handling after validation and final key assembly. It depends on `OMMetadataManager` table accessors, `BatchOperation`, `RepeatedOmKeyInfo`, and cleanup table declarations for replay/cache cleanup.

Risks and test signals: Completion is atomic only through the enclosing batch, so partial or out-of-order writes would corrupt MPU state. Tests should verify open key and MPU table deletion, committed key insertion, unused-part cleanup, bucket usage updates, overwrite behavior, and failure-response no-op semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCompleteResponse.java -->
