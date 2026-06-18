# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUploadCompleteInfo.java

Purpose: Response DTO for completing a multipart upload.

Important APIs/types/functions: Constructor stores volume, bucket, key, and hash/ETag. Deprecated getters expose volume/bucket/key; setters allow mutation. `getHash`/`setHash` expose the completion ETag.

Control flow and state: Mutable response object with no validation.

State and persistence behavior: Response only. Completed key metadata is persisted through normal key tables.

Dependencies and integration points: Used by complete MPU APIs and S3 ETag response mapping.

Risks: Mutable fields and deprecated accessors remain for compatibility. No validation of ETag/hash.

Test signals: Complete MPU response should verify ETag/hash and backward-compatible name fields.
