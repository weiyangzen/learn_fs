# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadAbortResponseWithFSO.java

Purpose: `S3MultipartUploadAbortResponseWithFSO` is the FSO-specific type for MPU abort responses.

Important APIs and types: It extends `S3MultipartUploadAbortResponse` and changes cleanup metadata to include `OPEN_FILE_TABLE` instead of `OPEN_KEY_TABLE`.

Control flow: It inherits abort DB behavior from the parent; constructor parameters provide the FSO multipart open key and bucket layout used by the shared helper.

State and persistence behavior: It deletes FSO open-file MPU state, deletes multipart info, queues parts in deleted table, and updates bucket table.

Dependencies and integration points: It integrates FSO abort request paths with common multipart abort persistence.

Risks and test signals: Tests should verify cleanup annotation, open-file table deletion, inherited failed response no-op, and part cleanup equivalence with default layout.
