## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadCommitPartRequestWithFSO.java

Purpose: `S3MultipartUploadCommitPartRequestWithFSO` adapts upload-part commit for FSO open file keys and response replay. It inherits commit logic and overrides table-key and lookup behavior.

Important APIs/types/functions: It overrides `getOpenKey` to build an `OmFSOFile` and call `getOpenFileName(clientID)`, `getOmKeyInfo` to use `OMFileRequest.getOmKeyInfoFromFileTable(true, ...)`, and `getOmClientResponse` to return `S3MultipartUploadCommitPartResponseWithFSO`.

Control flow: The base commit-part flow remains intact. The overridden open-key methods ensure the temporary uploaded part is found in the FSO open file table using volume/bucket/key path IDs rather than a flat key string.

State and persistence behavior: Multipart-info updates and open-key tombstones are inherited, but the FSO response class replays them against file/open-file table semantics. Delete-map cleanup and quota accounting remain the same conceptual state transitions as the base class.

Dependencies and integration points: It depends on `OmFSOFile`, `OMFileRequest`, `S3MultipartUploadCommitPartResponseWithFSO`, and the base commit-part request.

Risks and edge cases: Incorrect FSO open-key computation would make committed parts look missing. Response routing must preserve FSO-specific table behavior. Parent ID changes and nested paths rely on `OmFSOFile` to resolve correctly.

Test signals: Cover committing parts for nested FSO keys, overwriting FSO parts, missing FSO open-file rows, response replay, quota accounting, and delete-map cleanup.
