# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyDeleteRequestWithFSO.java

Purpose: `OMKeyDeleteRequestWithFSO` deletes a file or directory in an FSO bucket. It resolves the path to an `OzoneFileStatus`, tombstones either the file table or directory table, and supports recursive directory deletion checks at the single-request level.

Important APIs and types: The class extends `OMKeyDeleteRequest` and uses `OzoneFileStatus`, `OMFileRequest.getOMKeyInfoIfExists`, `OMFileRequest.hasChildren`, `OzoneFSUtils`, `OMKeyDeleteResponseWithFSO`, FSO path keys, and FSO ACL resolution via `resolveBucketAndCheckKeyAclsWithFSO`.

Control flow: `validateAndUpdateCache` acquires the bucket lock, validates volume/bucket, resolves the requested path to file or directory status, normalizes `OmKeyInfo` to the leaf file name, sets the update ID, computes the object-ID path key, rejects non-recursive deletion of a non-empty directory, tombstones directory table or key table based on status, decrements bucket quota and namespace, marks any associated hsync open-file entry with `DELETED_HSYNC_KEY`, enriches audit data for files, and returns an FSO delete response with the original user key name and directory flag.

State and persistence behavior: FSO deletion tombstones the directory table for directories and the key table for files, using `volumeId/bucketId/parentObjectId/leafName` DB keys. The response carries the volume ID and directory flag for batch operations. Bucket accounting uses the deleted object's block lengths and special empty-key handling. Hsync open-file entries are located by parent ID, file name, and hsync client ID.

Dependencies and integration points: It depends on FSO path lookup and child detection in `OMFileRequest`, bucket-level locking, file/directory table cache semantics, default replication config for status construction, audit/metrics inherited from delete request, and response code that persists tombstones and deleted-table entries.

Risks: A directory deletion with `recursive=true` tombstones only the requested directory entry here; broader recursive behavior must be coordinated by callers/services. Parent ID and leaf name must be preserved correctly when forming open-file and path keys. The class shares the hsync inconsistency warning risk with the base delete path. It does not override preExecute except ACL resolution, so path normalization assumptions must match FSO naming.

Test signals: `TestOMKeyDeleteRequestWithFSO` and `TestOMKeyDeleteResponseWithFSO` should cover file versus directory tombstones, non-empty directory failure without recursive flag, volume ID propagation, quota decrement for files and directories, hsync open-file marking, missing-key failure, and FSO ACL path checks.
