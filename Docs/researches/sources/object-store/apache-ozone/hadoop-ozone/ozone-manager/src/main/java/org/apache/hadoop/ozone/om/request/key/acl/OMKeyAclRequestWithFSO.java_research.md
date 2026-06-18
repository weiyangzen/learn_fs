## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyAclRequestWithFSO.java

Purpose: `OMKeyAclRequestWithFSO` is the FSO version of key ACL mutation handling. It extends `OMKeyAclRequest` but replaces flat-key lookup and cache updates with FSO file/directory status lookup and path-ID-based table writes.

Important APIs/types/functions: Its central method is `validateAndUpdateCache`. It uses `OMFileRequest.getOMKeyInfoIfExists`, `OzoneFileStatus`, `OzoneFSUtils.getFileName`, `OMFileRequest.getDirectoryInfo`, `OMKeyAclResponseWithFSO`, directory table, layout-specific key table, volume/bucket IDs, and the inherited subclass hooks. It adds an FSO-specific `onSuccess(..., boolean isDirectory, long volumeId, long bucketId)` callback.

Control flow: The request parses and resolves the path, checks WRITE_ACL if enabled, and acquires the bucket lock. It looks up the target with FSO-aware path traversal. Missing targets fail with `KEY_NOT_FOUND`. For mutation it resets the builder key name to the leaf file name, applies the subclass ACL operation, updates modification time and update ID, and then writes either a directory-table cache entry or file-table cache entry based on `OzoneFileStatus.isDirectory()`.

State and persistence behavior: FSO ACLs for directories are persisted as `OmDirectoryInfo` rows derived from `OmKeyInfo`; files are persisted as key-table rows keyed by `getOzonePathKey(volumeId, bucketId, parentObjectId, fileName)`. The response includes directory/file classification plus volume and bucket IDs so replay can update the correct table. Like the base class, writes are staged in cache under the transaction index.

Dependencies and integration points: This class connects key ACL APIs to the FSO namespace implementation, directory table, file table, bucket locks, linked-bucket resolution, and audit logging. Concrete FSO add/remove/set requests supply the same operation-specific parsing and response body as the flat-layout variants.

Risks and edge cases: The leaf-name reset is necessary because FSO DB rows store file names relative to a parent object ID; omitting it can corrupt row identity. Directories and files must be routed to different tables. The set-ACL modification-time branch does not check `operationResult`, unlike add/remove, matching current behavior but worth regression coverage.

Test signals: Useful tests include ACL updates on FSO files and directories, nested paths, missing paths, link buckets, modification-time behavior, directory-table replay, and ensuring responses carry `isDirectory`, volume ID, and bucket ID.
