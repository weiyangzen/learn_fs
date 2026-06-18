# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3InitiateMultipartUploadResponseWithFSO.java

Purpose: Tests initiating multipart upload for FILE_SYSTEM_OPTIMIZED layout.

Important APIs/types/functions: Uses `S3InitiateMultipartUploadResponseWithFSO`, `createS3InitiateMPUResponseFSO`, `getMultipartKey(volumeId,bucketId,parentID,fileName,uploadID)`, parent ID, `OmMultipartKeyInfo.getParentID`, and `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

Control flow: The test adds volume/bucket entries for ID lookup, supplies a synthetic parent ID and empty parent directory list, creates the FSO initiate response, commits, then verifies the open-file MPU record stores file name, parent ID, and multipart marker. It also verifies the multipart info table row uses the legacy multipart key and stores parent ID plus upload ID.

State/persistence: Writes one FSO open-file MPU row and one multipart info row.

Dependencies/integration: Integrates volume/bucket numeric IDs, FSO file-name extraction, and MPU metadata parent tracking.

Risks/test signals: Parent path directories are not actually created; parent ID is assumed. The test focuses on persistence shape and ID propagation.
