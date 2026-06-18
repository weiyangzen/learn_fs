# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/acl/prefix/TestOMPrefixAclResponse.java

Purpose: Tests prefix ACL response persistence and in-memory prefix manager reload.

Important APIs/types/functions: Uses `OMPrefixAclResponse`, `OmPrefixInfo`, `OzoneAcl`, `PrefixManagerImpl`, `OzoneObjInfo`, `prefixTable`, `SetAclResponse`, `RemoveAclResponse`, mocked `OzoneManager.resolveBucketLink`, and `ResolvedBucket`.

Control flow: The test creates two ACLs for `/vol/buck/prefix/`, writes them with a SetAcl response, commits, and verifies the prefix table. It creates a `PrefixManagerImpl` from the DB and verifies prefix info and ACL list. It then writes a RemoveAcl response leaving one ACL, reloads and verifies update ID and ACLs, and finally writes an empty ACL list and verifies the prefix table entry is removed.

State/persistence: Adds, updates, and removes rows in `prefixTable`. Also validates that persisted rows reconstruct the radix-tree-backed prefix manager state.

Dependencies/integration: Integrates security ACL types, OM prefix metadata, bucket-link resolution, and prefix manager loading.

Risks/test signals: Uses a mocked bucket resolver and one prefix path. It does not test failure responses. Strong signal is round-trip DB persistence plus manager reload behavior.
