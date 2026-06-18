## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadCompleteRequestWithFSO.java

Purpose: `S3MultipartUploadCompleteRequestWithFSO` specializes complete-MPU for FSO buckets. It overrides directory conflict checks, parent creation, file/open-file table lookup and cache writes, FSO DB key computation, multipart open-key computation, response classes, and bucket layout reporting.

Important APIs/types/functions: Overrides include `checkDirectoryAlreadyExists`, `addMissingParentsToCache`, `addMultiPartToCache`, `getOmKeyInfoFromKeyTable`, `getOmKeyInfoFromOpenKeyTable`, `addKeyTableCacheEntry`, `getDBOzoneKey`, `getDBMultipartOpenKey`, `getOmClientResponse`, and `getBucketLayout`. It uses `OMFileRequest.verifyDirectoryKeysInPath`, `getParentId`, `addDirectoryTableCacheEntries`, `addOpenFileTableCacheEntry`, `addFileTableCacheEntry`, and `S3MultipartUploadCompleteResponseWithFSO`.

Control flow: The inherited complete flow calls these overrides at layout-sensitive points. This subclass rejects completion if the target path is an existing directory, adds missing parent directories with namespace quota updates, writes synthesized missing multipart open-file state when needed, reads final/open keys through FSO file-table helpers, computes final file DB key from volume ID, bucket ID, parent ID, and leaf file name, and builds FSO responses carrying missing parent info and IDs.

State and persistence behavior: Final key state is written to the FSO file table, missing parents are written to the directory table, multipart open state is deleted from the FSO open file table, multipart-info is deleted from the common table, and bucket namespace changes include missing parents and possibly the final file. The response contains enough FSO identifiers for replay.

Dependencies and integration points: It connects base S3 complete-MPU validation to FSO directory hierarchy, namespace quota enforcement, file-table/open-file-table helpers, and FSO response replay.

Risks and edge cases: Correct final key identity depends on `getParentId` and leaf-name extraction. Missing parent creation during complete must not double-create rows already produced during initiate. Directory conflict handling must use FSO path traversal, not flat key checks. `getBucketLayout` always returns `FILE_SYSTEM_OPTIMIZED`, so this subclass should only be used for FSO routing.

Test signals: Cover nested FSO complete, missing parent creation, existing-directory target rejection, final file-table row, open-file and multipart-info deletion, unused part cleanup, namespace quota, and response replay with missing parent infos.
