# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadAbortRequestWithFSO.java

Purpose: adapts the abort-MPU tests to FSO layout. It inherits all behavioral tests from `TestS3MultipartUploadAbortRequest` and changes only request classes and key derivation.

Important APIs and types: `S3MultipartUploadAbortRequestWithFSO`, `S3InitiateMultipartUploadRequestWithFSO`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `OMRequestTestUtils.addParentsToDirTable`, `StringUtils.substringAfter`, `getOpenFileName`-style multipart key construction through metadata manager, and `UserGroupInformation`.

Control flow: inherited tests call overridden hooks. `getKeyName` returns `a/b/c/<uuid>`. `createParentPath` creates the directory hierarchy and stores `parentID`. `getMultipartOpenKey` strips the configured directory prefix, resolves volume and bucket IDs, and builds the FSO multipart open-file key from numeric IDs, parent ID, file name, and upload ID.

State and persistence behavior: logical `multipartInfoTable` rows still use volume/bucket/full-key/upload ID, while open-key table rows use FSO identity. The parent ID captured during directory creation is essential for locating the MPU open key during abort validation.

Dependencies and integration points: mirrors production FSO request subclasses and user context setup. It depends on the base class to seed and validate MPU state and on `OMRequestTestUtils` to make parent directories.

Risks covered: incorrect FSO open-key lookup during abort, mismatched parent IDs, and failure to delete FSO open-file rows. The class is intentionally small but important because inherited tests exercise success, missing, and orphan paths under FSO.

Test signals: inherited assertions pass with `BucketLayout.FILE_SYSTEM_OPTIMIZED`, including null multipart/open table rows after abort and correct error statuses for missing state.
