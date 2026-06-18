<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneNativeAuthorizer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneNativeAuthorizer.java

Purpose: broad parameterized coverage for native ACL evaluation across volume, bucket, key, and prefix resources.

Important APIs and functions: `data`, `createAll`, static `setup`, `createVolume`, `createBucket`, `createKey`, four parameterized `testCheckAccessFor*` methods, ACL mutation helpers, `resetAclsAndValidateAccess`, `getAclName`, `validateAll`, and `validateNone`.

Control flow: setup creates `OmTestManagers`, managers, write client, metadata manager, native authorizer, admin/test UGIs, and configures native authorizer class. Each parameter row creates a volume, bucket, and key or directory using randomized names, sets parent volume/bucket ACLs for child objects, then repeatedly resets object ACLs to each `ACLType`, checks authorizer decisions, adds additional ACLs, and verifies unavailable rights remain denied.

State and persistence behavior: test objects are persisted in OM test metadata; volume/bucket cache entries are mutated through `OzoneNativeAclTestUtil` while key/prefix ACLs go through `OzoneManagerProtocol`. Random names avoid collisions. Special cases skip `WRITE` and sometimes `CREATE` because those require open-key or non-existing-object semantics.

Dependencies and integration: `OmTestManagers`, OM managers, `OzoneManagerProtocol`, `OzoneAclUtil`, `OzoneObjInfo`, `RequestContext`, UGI, and AssertJ/JUnit parameterization. Risks include cache-vs-DB inconsistency, randomized identity type additions, and the `validateAll` loop building one context before changing rights. Test signals emphasize `ALL`, `NONE`, user/group/world/anonymous identities, parent ACL requirements, and admin allowance for volume create.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneNativeAuthorizer.java -->
