# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3InitiateMultipartUploadResponseWithFSO.java

Purpose: `S3InitiateMultipartUploadResponseWithFSO` persists MPU initiation for FSO buckets, including parent directory creation.

Important APIs and types: It extends `S3InitiateMultipartUploadResponse`, stores parent directory infos, MPU DB key, volume ID, bucket ID, and bucket info, and uses `OMFileRequest.addToOpenFileTableForMultipart`.

Control flow: It writes parent directories and bucket namespace state when parent dirs are present, writes the multipart open-file entry, then writes multipart info table using the precomputed MPU DB key.

State and persistence behavior: It mutates directory, bucket, open-file, and multipart info tables.

Dependencies and integration points: It integrates S3 MPU request handling with FSO object-ID keying and directory creation semantics.

Risks and test signals: Tests should cover parent creation, no-parent path, open-file multipart key format, multipart info key, bucket update, and failed response no-op.
