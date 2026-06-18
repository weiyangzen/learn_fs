# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadAbortResponse.java

Purpose: `S3MultipartUploadAbortResponse` persists aborting one MPU in default or layout-specific open-key storage.

Important APIs and types: It extends `AbstractS3MultipartAbortResponse`, stores multipart key, multipart open key, `OmMultipartKeyInfo`, bucket info, and bucket layout.

Control flow: `addToDBBatch` delegates to the singleton abort helper, which deletes open/multipart metadata, queues parts in deleted table, and updates bucket state.

State and persistence behavior: It removes one MPU's open-key and multipart-info entries and queues part blocks for deletion.

Dependencies and integration points: It is paired with S3 abort request handling and shared multipart abort logic.

Risks and test signals: Tests should cover aborting MPUs with multiple parts, empty parts, bucket used-byte update, failed response no-op, and correct open-key table selection.
