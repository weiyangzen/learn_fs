# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3MultipartUploadCompleteResponseWithFSO.java

Purpose: Tests completing multipart upload for FSO layout.

Important APIs/types/functions: Uses `S3MultipartUploadCompleteResponseWithFSO`, `S3MultipartUploadCommitPartResponse`, `createS3CompleteMPUResponseFSO`, `createS3CommitMPUResponseFSO`, `createS3InitiateMPUResponseFSO`, `OmMultipartKeyInfo`, `RepeatedOmKeyInfo`, FSO open/key/multipart keys, and `deletedTable`.

Control flow: Basic tests initiate an MPU, add an open file key, commit a part response, then complete MPU and verify the final key table row exists while multipart info and open MPU rows are removed. One variant passes null bucket info to validate that constructor path. Parts tests add committed and unused parts, then verify unused/replaced parts are in `deletedTable`. The preexisting-delete-table test seeds a deleted entry with the same logical key and verifies the newly completed object is not accidentally included in that existing delete record.

State/persistence: Completion promotes the final FSO key into `keyTable(FILE_SYSTEM_OPTIMIZED)`, removes multipart/open MPU metadata, and adds unused/replaced part metadata to `deletedTable`.

Dependencies/integration: Integrates parent directory creation, FSO object IDs, multipart part commit response, and deleted-table version merging semantics.

Risks/test signals: Several helper commits reuse the same fixture batch across phases, so batch lifecycle is subtle. The test does not cover legacy layout completion, only FSO. Strong signal is correct cleanup of MPU tables and no accidental deletion of the newly completed object.
