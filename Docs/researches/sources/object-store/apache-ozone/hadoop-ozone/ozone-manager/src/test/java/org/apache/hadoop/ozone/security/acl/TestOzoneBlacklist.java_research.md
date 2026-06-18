<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneBlacklist.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneBlacklist.java

Purpose: tests blacklist and read-blacklist precedence in `OzoneNativeAuthorizer`, including interaction with admin shortcuts.

Important APIs and functions: `testCreateVolume`, `testBucketOperation`, `testListAllVolume`, `testBlacklistedUserOperations`, `testBlacklistedGroupOperations`, `getUserRequestContext`, `getTestVolumeobj`, and `getTestBucketobj`.

Control flow: each test creates UGI test users/groups, sets admin or blacklist structures on a fresh authorizer, and calls `checkAccess`. Full blacklist entries deny matching users/groups even after admin access was granted. Read blacklist denies `LIST`, `READ`, and `READ_ACL` but leaves non-read operations to normal authorizer behavior. The bucket `WRITE` case asserts fall-through to null manager as a deliberate signal.

State and persistence behavior: no metadata persistence; mutable state lives in `OzoneNativeAuthorizer` admin, full blacklist, and read blacklist fields. UGI test state is reset after each test.

Dependencies and integration: `OzoneBlacklist`, `OzoneAdmins`, `UserGroupInformation`, `RequestContext`, and Ozone object builders. Risks include ordering bugs where admin checks might wrongly bypass blacklist checks or read blacklist might block writes. Test signals assert blacklist denial has higher precedence than admin allow for matching users/groups.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneBlacklist.java -->
