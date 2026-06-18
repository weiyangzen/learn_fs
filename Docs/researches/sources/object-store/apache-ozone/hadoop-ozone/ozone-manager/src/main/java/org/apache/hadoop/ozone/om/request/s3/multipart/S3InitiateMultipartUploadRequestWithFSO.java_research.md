## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3InitiateMultipartUploadRequestWithFSO.java

Purpose: `S3InitiateMultipartUploadRequestWithFSO` starts multipart uploads in FSO buckets. It extends the non-FSO initiate request but uses FSO directory traversal, parent object IDs, open file table keys, and missing-parent directory creation.

Important APIs/types/functions: Its overridden `validateAndUpdateCache` uses `OMFileRequest.verifyDirectoryKeysInPath`, `getAllMissingParentDirInfo`, `checkDirectoryResult`, `OMFileRequest.addDirectoryTableCacheEntries`, `OMFileRequest.addOpenFileTableCacheEntry`, `getMultipartKey(volumeId,bucketId,parentId,leaf,uploadId)`, and `S3InitiateMultipartUploadResponseWithFSO`.

Control flow: Under the bucket lock, it validates bucket/volume, verifies the directory path, rejects writes where the target is an existing directory, builds missing parent directory infos, computes both the flat multipart-info table key and the FSO open-file multipart key, resolves replication config, builds multipart info with object ID and parent ID, builds open `OmKeyInfo` with parent object ID, ACLs, metadata, tags, encryption, and owner, updates namespace quota for missing parents, writes parent directories, writes the open file entry, and writes the multipart-info entry.

State and persistence behavior: Missing parent directories are added to the directory table and bucket namespace usage is incremented. The open file table receives the future object under the FSO multipart open key, while multipart-info table uses the multipart key. The response carries missing parent infos, bucket copy, volume ID, and bucket ID for replay.

Dependencies and integration points: It integrates MPU initiation with FSO directory creation, namespace quota, parent object IDs, prefix ACL inheritance, replication config selection, encryption metadata, and the FSO response path.

Risks and edge cases: Existing directories with the target key name must fail with `NOT_A_FILE`. Parent directory creation changes namespace quota during initiation, so abort/cleanup paths must handle these rows consistently. Correct DB key computation depends on `lastKnownParentId` and `leafNodeName`.

Test signals: Cover nested MPU initiation creating missing parents, existing-directory target rejection, namespace quota increments, open-file and multipart-info cache rows, response replay, ACL inheritance, and metadata/tag/encryption propagation.
