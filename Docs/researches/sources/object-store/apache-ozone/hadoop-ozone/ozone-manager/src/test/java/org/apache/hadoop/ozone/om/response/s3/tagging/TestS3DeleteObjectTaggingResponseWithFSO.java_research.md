# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/tagging/TestS3DeleteObjectTaggingResponseWithFSO.java

Purpose: FSO specialization of delete-object-tagging response tests.

Important APIs/types/functions: Uses `S3DeleteObjectTaggingResponseWithFSO`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `addParentsToDirTable`, `addFileToKeyTable`, `getOzonePathKey`, and volume/bucket object IDs.

Control flow: Overrides key insertion to add volume/bucket, create parent directories, build an FSO key with tags and object IDs, write it to the file table, and return the FSO DB path. Overrides response construction to pass volume ID and bucket object ID. Inherited test verifies tags are cleared.

State/persistence: Replaces the FSO key-table row with tagless metadata.

Dependencies/integration: Integrates FSO path keying and tagging response subclass.

Risks/test signals: Parent path is empty, so nested FSO paths are not covered. No error response check.
