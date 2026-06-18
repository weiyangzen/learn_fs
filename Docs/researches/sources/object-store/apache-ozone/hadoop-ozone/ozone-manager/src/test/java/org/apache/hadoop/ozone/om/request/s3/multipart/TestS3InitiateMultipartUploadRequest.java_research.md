# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3InitiateMultipartUploadRequest.java

Purpose: tests default-layout `S3InitiateMultipartUploadRequest`, including pre-execution mutation, cache updates, error handling, metadata/tag propagation, and ACL inheritance from bucket default ACLs.

Important APIs and types: `S3InitiateMultipartUploadRequest`, `OmMultipartKeyInfo`, `OmKeyInfo`, `OmBucketInfo`, `OzoneAcl`, `OMRequestTestUtils.createInitiateMPURequest`, `getMultipartKey`, `getOpenKeyTable`, and `getMultipartInfoTable`. It inherits helper `doPreExecuteInitiateMPU` from `TestS3MultipartRequest`.

Control flow: `testPreExecute` only asserts that pre-execution adds upload ID and modification time. The success test creates a volume/bucket, sends custom metadata and tags, pre-executes, validates, and then reads the open-key table and multipart-info table for the multipart DB key. Negative tests add only a volume or neither volume nor bucket and expect not-found status with no state created.

State and persistence behavior: success creates an open MPU key in the layout-specific open-key table and a matching `multipartInfoTable` entry. `OmKeyInfo.latestVersionLocations` must be marked multipart, metadata and tags must match request input, creation and modification time must be the pre-execute modification time, and the multipart row upload ID must match the response request ID.

Dependencies and integration points: bucket default ACL inheritance is checked by creating an `OmBucketInfo` with DEFAULT and ACCESS ACLs. The new key must inherit only parent DEFAULT ACLs, converted to ACCESS scope; existing parent ACCESS ACLs must not be inherited.

Risks covered: missing metadata/tag carryover, writing multipart rows on failed volume/bucket lookup, wrong upload ID, timestamps not aligned with pre-execute, and ACL scope confusion.

Test signals: `Status.OK`, `BUCKET_NOT_FOUND`, `VOLUME_NOT_FOUND`, non-null open/multipart table entries on success, null entries on failure, `isMultipartKey == true`, and exact ACL containment/exclusion.
