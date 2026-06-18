<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestVolumeOwner.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestVolumeOwner.java

Purpose: tests volume-owner authorization rules in `OzoneNativeAuthorizer` for volume, bucket, and key operations.

Important APIs and functions: static `setup`, `prepareTestVols`, `prepareTestBuckets`, `prepareTestKeys`, `testVolumeOps`, `testBucketOps`, `testKeyOps`, `getUserRequestContext`, object-name helpers, object builders, and `getAclsToTest`.

Control flow: setup creates two volumes with distinct owners, two buckets under each, and two keys under each bucket. One key gets `ALL` ACLs for `testUgi`; the other gets `NONE`, allowing owner behavior to be tested independent of direct key ACLs. Volume tests assert admins can create, non-admin non-owners cannot create, volume owners still cannot perform admin `CREATE`, and owners can perform all non-`CREATE`/non-`NONE` operations. Bucket/key tests assert matching volume owner is allowed without object ACLs while non-owner is denied.

State and persistence behavior: OM test metadata persists volumes, buckets, and committed keys. `RequestContext.ownerName` is the main owner signal; the local `isOwner` parameter is unused and only expresses intent in call sites.

Dependencies and integration: `OmTestManagers`, native authorizer managers, `OzoneAclUtil`, `StandaloneReplicationConfig`, `OzoneManagerProtocol`, UGI, and JUnit. Risks include conflating request-supplied ownerName with looked-up volume ownership, and the unused helper parameter hiding assertion intent. Test signals clarify that volume owners have broad non-admin access to child buckets/keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestVolumeOwner.java -->
