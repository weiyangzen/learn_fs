# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/acl/TestOMBucketRemoveAclRequest.java

Tests `OMBucketRemoveAclRequest` for preExecute mutation, add-then-remove ACL behavior, and missing-bucket failure.

Important APIs are `OMRequestTestUtils.createBucketRemoveAclRequest`, `createBucketAddAclRequest`, `OMBucketAddAclRequest`, `OMBucketRemoveAclRequest`, `OzoneAcl`, `OMClientResponse`, and `bucketTable`. The success test seeds user, volume, and bucket state, adds an ACL through the add request, verifies one ACL exists, then removes it through the remove request and verifies the ACL list is empty. Transaction indexes differ between add and remove to exercise ordered cache updates.

Persistence behavior is two mutations of the same `OmBucketInfo`: ACL list size 0 -> 1 -> 0. The missing-bucket path returns `BUCKET_NOT_FOUND` without creating state. Risks include stale ACL retention, false success without table mutation, and untested duplicate/absent-ACL cases. Signals are increased preExecute modification time, `Status.OK` for add and remove, exact ACL list sizes, and `BUCKET_NOT_FOUND`.
