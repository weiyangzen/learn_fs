# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3MultipartUploadAbortResponseWithFSO.java

Purpose: FSO specialization of single MPU abort tests.

Important APIs/types/functions: Overrides `getKeyName`, `getBucketLayout`, `getMultipartOpenKey`, FSO initiate response creation, abort response creation, and part creation. Uses `S3MultipartUploadAbortResponseWithFSO`, `S3InitiateMultipartUploadResponseWithFSO`, `OzoneFSUtils.getFileName`, and numeric FSO multipart open keys.

Control flow: Inherited abort tests run with keys under `abort/b/c/`, a synthetic parent ID, FSO open MPU key computation, and FSO-specific part names. The subclass ensures the response removes FSO open-file MPU rows and writes part cleanup entries using FSO part key info.

State/persistence: Mutates FSO open key table, `multipartInfoTable`, and `deletedTable`.

Dependencies/integration: Integrates Apache Commons `StringUtils.substringAfter` for file-name extraction and FSO volume/bucket ID lookups.

Risks/test signals: Parent ID is synthetic and parent directories are not created. The subclass is focused on key construction and table placement rather than request validation.
