# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/tagging/TestS3PutObjectTaggingResponseWithFSO.java

Purpose: FSO specialization of put-object-tagging response tests.

Important APIs/types/functions: Uses `S3PutObjectTaggingResponseWithFSO`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `addParentsToDirTable`, `addFileToKeyTable`, `getOzonePathKey`, and FSO object IDs.

Control flow: Overrides setup to add volume/bucket, create parent dirs, create an FSO key info, write it to file table, and return the FSO DB key. Overrides response construction to include volume ID and bucket object ID. Inherited test verifies tag update persistence.

State/persistence: Updates the FSO key table row with supplied tags.

Dependencies/integration: Covers FSO subclass and numeric path DB keying for object tagging.

Risks/test signals: Empty parent path only; nested path behavior is not tested. It inherits limited value checking from the default tagging test.
