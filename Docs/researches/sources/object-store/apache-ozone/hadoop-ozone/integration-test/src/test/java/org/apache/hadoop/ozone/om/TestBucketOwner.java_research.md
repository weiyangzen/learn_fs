# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestBucketOwner.java

## Purpose
`TestBucketOwner` validates authorization semantics for bucket owners, volume owners, and unrelated users. It ensures bucket owners and volume owners can perform key and ACL operations while non-owners cannot.

## Important APIs, Types, and Functions
- `init()` creates three test users, creates a volume as admin, sets volume owner and world ACL, then logs in as user1 to create three buckets owned by user1.
- `testBucketOwner()` checks user1 can create/delete keys, delete a bucket, list keys, get ACLs, and add ACLs.
- `testNonBucketNonVolumeOwner()` checks user3 cannot create/delete/rename/list keys or get/add ACLs.
- `testVolumeOwner()` checks user2, the volume owner, can create/delete keys, list keys, manage ACLs, and delete a bucket.
- `createVolumeWithOwnerAndAcl(...)` and `setVolumeAcl(...)` set owner and ACL state through client protocol and object ACL APIs.

## Control Flow
The tests repeatedly set `UserGroupInformation` login user, create clients under that identity, and execute operations against the same volume/buckets. Positive cases simply execute operations, while negative cases wrap each operation in `assertThrows`.

## State and Persistence Behavior
Persistent state includes volume owner, bucket owner, world volume ACL, bucket metadata, keys, and ACL entries. The static login user is process-wide state and is deliberately changed between setup and tests.

## Dependencies and Integration Points
Dependencies include `AclTests.ADMIN_UGI`, `UserGroupInformation`, Ozone client APIs, `ClientProtocol.setVolumeOwner`, Ozone ACL parsing/building, `OzoneObjInfo`, and `TestDataUtil.createKey`.

## Risks and Test Signals
Risks include global login-user leakage and broad `assertThrows(Exception.class)` hiding exact authorization error types. Signals are positive operation completion for bucket/volume owners and exceptions for a non-owner/non-volume-owner.
