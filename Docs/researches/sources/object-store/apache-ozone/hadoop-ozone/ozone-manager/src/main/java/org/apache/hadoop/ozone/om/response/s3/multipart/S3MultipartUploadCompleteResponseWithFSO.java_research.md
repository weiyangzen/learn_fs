<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCompleteResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCompleteResponseWithFSO.java

Purpose: FSO variant of complete-MPU response. It commits the final object into the file table and creates any missing parent directory entries required by S3 path semantics over an FSO bucket.

Important APIs/types/functions: Extends `S3MultipartUploadCompleteResponse`. The success constructor adds `volumeId`, `bucketId`, `missingParentInfos`, and `multipartKeyInfo`. It overrides `addToDBBatch` and `addToKeyTable`. It uses `OMFileRequest.addToFileTable`, `OMFileRequest.addToOpenFileTableForMultipart`, and `OMFileRequest.getOmKeyInfoFromFileTable`.

Control flow and persistence: If parent directories are missing, it writes each `OmDirectoryInfo` to `DirectoryTable` under an object-ID path key, updates bucket table namespace accounting, and, when an existing file table entry is detected for the multipart key, re-adds multipart open-file metadata. It then delegates to the base class to delete open-file and MPU entries, add the final file, schedule unused parts, and update bucket accounting.

Dependencies and integration: Integrated by complete-MPU requests for `FILE_SYSTEM_OPTIMIZED` buckets. It depends on FSO object IDs, directory-table semantics, and the base completion flow for common MPU cleanup.

Risks and test signals: Parent directory creation and open-file restoration are subtle because they interact with overwrite and missing-parent flows. Tests should cover nested S3 keys in FSO buckets, overwrite of existing files, deleted unused parts, bucket namespace/bytes changes, and failure constructor no-op behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCompleteResponseWithFSO.java -->
