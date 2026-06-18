# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/acl/TestOMBucketAddAclRequest.java

Tests `OMBucketAddAclRequest` for preExecute modification time changes, successful ACL persistence, and missing-bucket failure.

The test uses `OMRequestTestUtils.createBucketAddAclRequest`, `OzoneAcl.parseAcl`, `OMClientResponse`, `OMResponse.getAddAclResponse`, and the shared `TestBucketRequest` fixture. PreExecute records the original add-ACL modification time, calls `preExecute`, and asserts a different request with a greater timestamp. The success path seeds user, volume, and bucket rows; validates the add request; then reads `bucketTable` to assert exactly one persisted ACL matching `user:newUser:rw`. The failure path validates without a bucket and expects `BUCKET_NOT_FOUND`.

State behavior is mutation of `OmBucketInfo` ACL list in `bucketTable`. Dependencies are OM ACL request helpers, bucket metadata persistence, and protobuf response statuses. Risks not covered include duplicate ACLs, absent-user authorization behavior, and link buckets. Signals are newer modification time, `Status.OK`, non-null add response, one ACL in the bucket row, and `BUCKET_NOT_FOUND` when absent.
