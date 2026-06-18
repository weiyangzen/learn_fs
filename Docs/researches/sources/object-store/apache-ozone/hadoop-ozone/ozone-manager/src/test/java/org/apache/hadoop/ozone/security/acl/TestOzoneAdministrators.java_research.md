<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneAdministrators.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneAdministrators.java

Purpose: verifies `OzoneNativeAuthorizer` administrator and read-only administrator shortcuts for volume, bucket, and root volume listing operations.

Important APIs and functions: `testCreateVolume`, `testBucketOperation`, `testListAllVolume`, helper predicate factories backed by `OzoneAdmins`, `testAdminOperations`, `testGroupAdminOperations`, `getUserRequestContext`, `getTestVolumeobj`, and `getTestBucketobj`.

Control flow: tests create UGI test users/groups, build `OzoneObjInfo` instances, install admin/read-only-admin predicates on a shared `OzoneNativeAuthorizer`, then call `checkAccess` with `CREATE`, `LIST`, `READ`, `READ_ACL`, or `WRITE`. Positive cases cover wildcard admins, matching users, matching groups, and read-only admin read operations. Negative cases cover empty/mismatched admin lists and read-only admins attempting create.

State and persistence behavior: no OM metadata managers are configured, so some non-shortcut write paths intentionally fall through to null manager access and assert `NullPointerException`. The important state is the mutable authorizer admin predicate fields and global UGI test registry, reset in `finally`.

Dependencies and integration: `OzoneAdmins`, `UserGroupInformation`, `OzoneObjInfo`, `RequestContext`, and `OMException`. Risks include shared static `nativeAuthorizer` retaining predicates between tests and assertions depending on null managers. Test signals explicitly document precedence: full admins bypass ACL checks, read-only admins only bypass read-like operations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneAdministrators.java -->
