<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestParentAcl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestParentAcl.java

Purpose: verifies native authorizer parent ACL requirements when accessing buckets and keys. It confirms child ACL alone is insufficient and access requires suitable parent or grandparent rights.

Important APIs and functions: static `setup`, `testKeyAcl`, `testBucketAcl`, `testParentChild`, `resetAcl`, ACL mutation helpers backed by `OzoneNativeAclTestUtil`, and object creation helpers. `testKeyAcl` is marked `@Unhealthy("HDDS-6335")`, a significant signal that key-path parent ACL behavior is known problematic.

Control flow: setup creates an OM test environment and native authorizer. Tests create randomized volumes/buckets/keys, snapshot original ACLs, then run `testParentChild` with combinations like parent `READ` plus child `WRITE_ACL`, `DELETE`, `READ_ACL`, `LIST`, and parent `WRITE` plus child `CREATE`/`WRITE`. For buckets, bucket ACL alone denies until volume ACL is added. For keys, key ACL and bucket ACL deny until volume ACL is also added.

State and persistence behavior: OM metadata tables hold volume, bucket, and key ACL state. The test repeatedly resets ACLs to avoid cross-case leakage. There is an apparent risk in `testKeyAcl`: `originalKeyAcls` is loaded from bucket ACLs, not key ACLs, which may weaken reset fidelity.

Dependencies and integration: `OmTestManagers`, OM managers, write client, `OzoneAcl`, `BucketLayout.DEFAULT`, `OzoneManagerProtocol`, UGI, and `@Unhealthy`. Risks include known HDDS-6335 instability, direct cache mutation, and parent ACL semantics diverging between bucket and key code paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestParentAcl.java -->
