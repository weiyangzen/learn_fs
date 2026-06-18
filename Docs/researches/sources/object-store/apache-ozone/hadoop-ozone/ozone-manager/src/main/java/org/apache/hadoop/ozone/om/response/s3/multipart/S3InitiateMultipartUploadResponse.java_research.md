# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3InitiateMultipartUploadResponse.java

Purpose: `S3InitiateMultipartUploadResponse` persists initial MPU state for default/non-FSO layouts.

Important APIs and types: It extends `OmKeyResponse`, stores `OmMultipartKeyInfo` and `OmKeyInfo`, cleans `OPEN_KEY_TABLE` and `MULTIPART_INFO_TABLE`, and exposes testing getters.

Control flow: It derives the multipart key from volume, bucket, key, and upload ID, writes open-key table state, and writes multipart info table state with the same key.

State and persistence behavior: It creates the in-progress MPU open key and multipart metadata but does not write committed key data.

Dependencies and integration points: It integrates S3 initiate MPU request handling, open key table, multipart info table, and later commit/abort/complete operations.

Risks and test signals: Tests should verify multipart key format, both table writes, bucket layout routing, failed response no-op, and getter payloads.
