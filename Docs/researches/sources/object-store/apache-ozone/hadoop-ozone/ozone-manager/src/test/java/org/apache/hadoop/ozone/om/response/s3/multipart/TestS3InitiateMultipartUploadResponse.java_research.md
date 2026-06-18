# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3InitiateMultipartUploadResponse.java

Purpose: Tests initiating a multipart upload for the default layout.

Important APIs/types/functions: Extends `TestS3MultipartResponse`; uses `S3InitiateMultipartUploadResponse`, `createS3InitiateMPUResponse`, open key table, `multipartInfoTable`, `OmKeyInfo.getLatestVersionLocations().isMultipartKey`, and upload ID.

Control flow: The test creates random volume/bucket/key/upload ID, obtains a response from the base helper, adds it to a batch, commits, computes the multipart DB key, and verifies an open MPU key and multipart info row exist with expected multipart flag and upload ID.

State/persistence: Writes to the default open key table and `multipartInfoTable` under the same multipart key.

Dependencies/integration: Uses base MPU fixture and protobuf response builders.

Risks/test signals: Does not add volume/bucket rows because legacy initiate helper does not need numeric IDs. It does not test error response behavior.
