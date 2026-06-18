# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadCompleteRequestWithFSO.java

Purpose: specializes complete-MPU tests for FSO layout. It inherits default complete-MPU scenarios and overrides key generation, parent directory handling, final key-table lookup, request factories, and namespace expectations.

Important APIs and types: `S3MultipartUploadCompleteRequestWithFSO`, `S3MultipartUploadCommitPartRequestWithFSO`, `S3InitiateMultipartUploadRequestWithFSO`, `OMFileRequest.getParentID`, `OzoneFSUtils`, `OmKeyInfo`, `OmKeyLocationInfoGroup`, `OMRequestTestUtils.addFileToKeyTable`, and FSO metadata-manager path-key methods.

Control flow: `getKeyName` returns a random parent directory plus `a/b/c/file1`. `addKeyToTable` resolves/creates the parent directory through `getParentID`, builds open-file `OmKeyInfo` with leaf file name and parent/object IDs, and writes it to the FSO open-file table. Inherited tests then initiate, commit, and complete MPU. `getOzoneDBKey` resolves the final key-table row using volume ID, bucket ID, parent ID, and file name.

State and persistence behavior: final completed object lands in the FSO key table under an ozone path key, not the legacy ozone key. Namespace count is expected to be `5L`, reflecting the file plus parent directories created by the FSO workflow. Open multipart and multipart-info cleanup still occurs through inherited assertions.

Dependencies and integration points: request factory overrides instantiate FSO subclasses and set current-user UGI. Parent resolution depends on `OMFileRequest.getParentID` after directories are created by initiate or helper setup.

Risks covered: wrong final key table key, lost parent ID, full path stored as file name, namespace undercount for created parent directories, and mismatch between FSO commit and complete request classes.

Test signals: inherited complete-MPU statuses and table assertions, plus FSO namespace count `5L` and final closed key lookup via `getOzonePathKey`.
