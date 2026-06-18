# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmMultipartUpload.java

Purpose: tests parsing of multipart upload database keys into `OmMultipartUpload` fields.

Important APIs/types/functions: covers `OmMultipartUpload.getDbKey`, `OmMultipartUpload.from`, and getters for volume, bucket, key, and upload ID.

Control flow and state: builds a DB key for `vol1/bucket1/dir1/key1/uploadId`, parses it, and asserts all components including a nested key path are preserved.

Dependencies and integration points: this helper underpins OM multipart upload table key parsing and S3 MPU request handling.

Risks and test signals: catches delimiter parsing errors where object keys contain slashes. Coverage is narrow and does not test malformed keys or upload IDs containing delimiter-like content.
