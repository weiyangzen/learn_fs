# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/acl/TestOMBucketSetAclRequest.java

Tests `OMBucketSetAclRequest` replacement semantics. It verifies preExecute modification time advancement, successful replacement with user and group ACLs, and missing-bucket failure.

The test builds requests with `OMRequestTestUtils.createBucketSetAclRequest` and Guava `Lists.newArrayList`. The success path seeds owner/user plus volume/bucket rows, validates a set request containing `user:newUser:rw` and `group:newGroup:rw`, then reads `bucketTable` and checks the persisted ACL list size and ordering. The failure path validates with no bucket and expects `BUCKET_NOT_FOUND`.

State behavior is full replacement of the bucket ACL list, not append/remove. Dependencies include Ozone ACL parsing, bucket metadata table, protobuf set-ACL response, and the shared bucket fixture. Risks are appending instead of replacing, reordered ACLs, no modification time update, and untested empty/duplicate ACL lists. Signals are newer modification time, non-null `SetAclResponse`, `Status.OK`, exact persisted ACLs, and `BUCKET_NOT_FOUND`.
