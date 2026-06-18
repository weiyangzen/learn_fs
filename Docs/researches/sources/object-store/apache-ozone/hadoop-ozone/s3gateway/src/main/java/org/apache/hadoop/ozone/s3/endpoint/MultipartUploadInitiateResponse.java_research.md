# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MultipartUploadInitiateResponse.java

Purpose: `MultipartUploadInitiateResponse` is the JAXB XML result for initiating a multipart upload.

Important APIs and flow: fields are `Bucket`, `Key`, and `UploadId`. The object endpoint fills them after Ozone creates a multipart upload record.

State, dependencies, risks, and tests: state is response-only. It integrates with object PUT `?uploads` handling. Risks include missing URL encoding for keys and null upload IDs if Ozone initiation fails before response creation. Tests should assert XML shape and correct bucket/key/upload ID values.
