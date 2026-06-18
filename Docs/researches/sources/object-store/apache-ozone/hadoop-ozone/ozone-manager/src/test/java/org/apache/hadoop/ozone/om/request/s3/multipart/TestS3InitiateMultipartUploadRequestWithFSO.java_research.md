# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3InitiateMultipartUploadRequestWithFSO.java

Purpose: extends initiate-MPU tests for `BucketLayout.FILE_SYSTEM_OPTIMIZED`. It verifies parent directory creation, FSO open-file key construction, multipart table parent ID, metadata/tag propagation, and default ACL inheritance through generated directories.

Important APIs and types: `S3InitiateMultipartUploadRequestWithFSO`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `OmDirectoryInfo`, `OmMultipartKeyInfo`, `OmKeyInfo`, `UserGroupInformation`, and metadata-manager methods `getOzonePathKey`, `getMultipartKey(volumeId,bucketId,parentId,fileName,uploadId)`, and logical `getMultipartKey(volume,bucket,key,uploadId)`.

Control flow: the success test creates volume/bucket metadata, uses key path `a/b/c/<file>`, pre-executes through FSO helpers, validates the request, then walks the expected `a`, `b`, `c` directory rows. It compares the logical multipart key in `multipartInfoTable` with the FSO open-file multipart key in `openKeyTable`.

State and persistence behavior: request validation creates directory-table entries for missing parents, writes an FSO open MPU file under the resolved parent object ID, and records `parentID` in `OmMultipartKeyInfo`. The stored file name is the leaf file name, not the full path. Metadata/tags and creation/modification times match the pre-executed request.

Dependencies and integration points: overrides `getS3InitiateMultipartUploadReq` to instantiate the FSO request and set a login UGI. ACL inheritance checks that each created directory inherits parent DEFAULT ACLs as DEFAULT ACLs, while the leaf file inherits final parent DEFAULT ACLs converted to ACCESS scope.

Risks covered: wrong split between logical MPU table keys and FSO open-file table keys, missing parent directory creation, incorrect `parentID`, failure to preserve tags/metadata, and ACL inheritance drift across directory levels.

Test signals: `Status.OK`, non-null directory/open/multipart rows, expected directory paths like `parentID/name`, matching parent object IDs, leaf file name equality, timestamp equality, and exact inherited ACL lists.
