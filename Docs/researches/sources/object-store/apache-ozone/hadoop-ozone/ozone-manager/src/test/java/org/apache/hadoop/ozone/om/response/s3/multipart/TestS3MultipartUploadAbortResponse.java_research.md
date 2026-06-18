# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3MultipartUploadAbortResponse.java

Purpose: Tests aborting a single multipart upload in the default layout.

Important APIs/types/functions: Uses `S3MultipartUploadAbortResponse`, `S3InitiateMultipartUploadResponse`, `multipartInfoTable`, open key table, `deletedTable`, `PartKeyInfo`, `RepeatedOmKeyInfo`, and `getOzoneDeletePathKey`.

Control flow: First test initiates an MPU, verifies open and multipart rows exist, aborts it, commits, then verifies both rows are gone and deleted table is empty because there are no parts. Second test adds two dummy parts to the multipart info before abort and verifies two deleted-table rows contain the corresponding part key infos.

State/persistence: Abort removes open MPU and multipart info rows. Part-bearing abort moves part metadata to `deletedTable` for block cleanup.

Dependencies/integration: Relies on base MPU response factories and OM multipart key naming.

Risks/test signals: One assertion in the parts test checks open key table by `multipartKey` instead of `multipartOpenKey`, which is equivalent only in default layout. It does not exercise error responses.
