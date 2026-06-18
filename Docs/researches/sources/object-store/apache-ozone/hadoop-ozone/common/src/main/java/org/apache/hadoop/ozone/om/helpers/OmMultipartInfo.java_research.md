# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartInfo.java

Purpose: Response DTO for initiating a multipart upload.

Important APIs/types/functions: Constructor stores volume, bucket, key, and upload ID. Deprecated getters expose volume, bucket, and key; `getUploadID` is the main current accessor.

Control flow and state: Simple mutable-field DTO with no setters.

State and persistence behavior: Response only. Initiation state is persisted elsewhere as multipart metadata.

Dependencies and integration points: Used by initiate multipart upload APIs, including older clients that still read volume/bucket/key fields.

Risks: Deprecated fields remain for compatibility. No validation of upload ID or names.

Test signals: Initiate MPU response tests should verify upload ID and backward-compatible field values.
