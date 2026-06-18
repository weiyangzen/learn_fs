<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/OzoneNativeAclTestUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/OzoneNativeAclTestUtil.java

Purpose: package-private helper for native ACL tests that mutates OM metadata tables directly. It exists because several older ACL APIs update persistent DB state without the in-memory cache path used by authorizer tests.

Important APIs and functions: `addVolumeAcl`, `addBucketAcl`, `addKeyAcl`, `setVolumeAcl`, `setBucketAcl`, `setKeyAcl`, `getVolumeAcls`, `getBucketAcls`, and `getKeyAcls`. Each setter reads the relevant `OmVolumeArgs`, `OmBucketInfo`, or `OmKeyInfo`, rebuilds it through a builder, and writes a `CacheValue` into the metadata table under a `CacheKey`.

Control flow: callers compute volume/bucket/key identifiers, retrieve table entries from `OMMetadataManager`, mutate ACL lists through builder methods, then add a cache entry at transaction index `1L`. Getter methods read directly from the relevant table and return the stored ACL list.

State and persistence behavior: this utility deliberately bypasses request handling and writes OM metadata table caches, not external filesystem state. It depends on existing rows being present; missing rows would cause null dereferences before assertions. It also assumes `BucketLayout` is passed correctly for key table selection.

Dependencies and integration: `OMMetadataManager`, HDDS table/cache APIs, `OzoneAcl`, bucket layouts, and OM helper types. Risks include stale cache/DB divergence, fixed transaction index reuse, and tests masking production paths by direct cache mutation. Test signal is indirect: native authorizer tests use these methods to set precise ACL preconditions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/OzoneNativeAclTestUtil.java -->
