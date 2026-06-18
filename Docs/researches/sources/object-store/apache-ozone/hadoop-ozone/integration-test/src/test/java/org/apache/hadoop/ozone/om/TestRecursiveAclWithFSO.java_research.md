# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestRecursiveAclWithFSO.java

## Purpose
Abstract non-HA integration tests for recursive ACL enforcement and default ACL assignment in FILE_SYSTEM_OPTIMIZED buckets. It focuses on directory delete/rename permission checks that must inspect descendants, not just the requested parent path.

## Important APIs and Types
The class `TestRecursiveAclWithFSO` implements `NonHATests.TestCase`. Important tests are `testKeyDeleteAndRenameWithoutPermission` and `testKeyDefaultACL`. Helpers include `removeAclsFromKey`, `createVolumeWithOwnerAndAcl`, `setVolumeAcl`, `addVolumeAcl`, `setBucketAcl`, `setKeyAcl`, and `createKeys`. It uses `UserGroupInformation`, `ObjectStore`, `OzoneBucket`, `OzoneVolume`, `OzoneObjInfo`, `OzoneAcl`, `BucketArgs`, and `OMException.ResultCodes.PERMISSION_DENIED`.

## Control Flow
The permission test creates a volume owned by one test user, grants broad world ACLs, builds a multi-level FSO tree, then removes ACLs from a child file or child directory. A second user attempts recursive delete and rename on ancestor directories and must receive permission-denied errors. The default ACL test creates a volume, bucket, and key under different login users and asserts owner/group default ACL entries match `OmConfig` defaults.

## State and Persistence
Persistent OM state includes volume ownership, bucket and key ACL rows, FSO directory/key metadata, and default ACL entries. The test mutates the global/login UGI, so request identity is part of the test state. Removing all ACLs from a descendant should persist and influence later recursive operations on ancestors.

## Dependencies and Integration Points
This ties together OM ACL manager behavior, FSO path resolution, recursive directory delete/rename paths, Ozone object-store clients, `OzoneObj` ACL APIs, and Hadoop UGI identity.

## Risks and Edge Cases
The test depends on process-wide login user changes and must be isolated by the surrounding cluster provider. One created user has a group string containing a comma inside a single group array entry, which may be intentional but is easy to misread. Recursive ACL traversal can be expensive and timing-sensitive in larger trees; this test uses a compact but branching tree.

## Test Signals
Signals include permission denial when any descendant lacks needed access, denial for a directory where the acting user has no ACLs, correct default volume ACLs for admin user and group, and correct default bucket/key ACLs for the active user and primary group.
