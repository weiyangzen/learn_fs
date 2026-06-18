# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestObjectStoreWithLegacyFS.java

Purpose: This abstract non-HA integration test verifies legacy filesystem-path behavior when OM filesystem paths are enabled, especially the distinction between flat `OBJECT_STORE` buckets and path-like `LEGACY` buckets. It also tests multipart upload completion when directory-like keys already exist.

Important APIs and types: The file uses `OmConfig.isFileSystemPathEnabled`, `setFileSystemPathEnabled`, `OzoneClient`, `OzoneVolume`, `OzoneBucket`, `BucketArgs`, `BucketLayout.OBJECT_STORE`, `BucketLayout.LEGACY`, `Table<String, OmKeyInfo>`, `RatisReplicationConfig`, `OmMultipartInfo`, `OmMultipartCommitUploadPartInfo`, `OmMultipartUploadCompleteInfo`, `OzoneConsts.ETAG`, MD5 ETags, and `OMException.ResultCodes.NOT_A_FILE`.

Control flow: `initClass` records and enables the OM filesystem path flag, and `cleanup` restores it. Each test creates a fresh object-store-layout bucket. `testFlatKeyStructureWithOBS` creates a nested key in an OBS bucket, iterates the object-store key table from a prefix, verifies only the flat key exists, renames it, and verifies the flat row changed without intermediate directory rows. `testMultiPartCompleteUpload` uploads one MPU part to an OBS bucket while a trailing-slash key exists and expects success, then repeats in a LEGACY bucket with a directory-like conflicting path and expects failure.

State and persistence behavior: Persistent state includes OM key table rows, renamed flat key names, multipart upload state, part ETags, and layout-specific interpretation of trailing slash keys. The key-table iterator check ensures OBS remains a flat key-value structure even when filesystem paths are globally enabled.

Dependencies and integration points: It integrates object-store bucket operations, OM runtime config mutation, metadata table iteration, key rename, multipart upload initiation/part creation/completion, replication config, and legacy directory conflict detection.

Risks: The test mutates shared OM config and must restore it to avoid leaking filesystem-path behavior into later tests. Iterator prefix counting is sensitive to DB key encoding. MPU behavior depends on MD5 ETag metadata being set on the output stream before close.

Test signals: Signals include exactly one matching OBS key row before and after rename, successful OBS MPU completion despite a trailing-slash key, `NOT_A_FILE` for LEGACY MPU completion with a conflicting directory-like path, non-null upload IDs and completion info, and restored filesystem-path config after the class.
