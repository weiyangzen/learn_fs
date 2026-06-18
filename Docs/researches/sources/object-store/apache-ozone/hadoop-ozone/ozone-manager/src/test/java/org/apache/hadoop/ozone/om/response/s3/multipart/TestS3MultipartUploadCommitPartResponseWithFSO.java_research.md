# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3MultipartUploadCommitPartResponseWithFSO.java

Purpose: Tests committing multipart upload parts for FSO layout.

Important APIs/types/functions: Uses `S3MultipartUploadCommitPartResponseWithFSO`, `createS3CommitMPUResponseFSO`, `createS3InitiateMPUResponseFSO`, `createPartKeyInfoFSO`, `addParentsToDirTable`, `multipartInfoTable`, open key table, and `deletedTable`.

Control flow: Basic success test creates volume/bucket and parent path, computes an open file key, commits a part without an old part, and verifies the open key is removed, multipart info remains, and deleted table stays empty. Parts test initiates MPU, adds an old part, commits a replacement, and verifies old part metadata is written to deleted table. Error test uses `NO_SUCH_MULTIPART_UPLOAD_ERROR` with an invalid key and verifies open-key cleanup is still recorded in deleted table.

State/persistence: Removes the committed open part key, updates or creates multipart info, and moves replaced/error open part metadata to `deletedTable`.

Dependencies/integration: Exercises FSO parent path creation, multipart key naming, part protobuf conversion, and delete path computation.

Risks/test signals: Some assertions inspect tables before committing the batch, relying on cache/batch behavior. It is FSO-only; legacy commit-part behavior is not represented here.
