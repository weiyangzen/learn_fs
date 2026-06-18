# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/PrefixManagerImpl.java

Purpose: `PrefixManagerImpl` implements prefix ACL storage, lookup, inheritance, and access checks. It keeps an in-memory `RadixTree<OmPrefixInfo>` synchronized with `prefixTable` so OM can evaluate prefix ACLs without scanning RocksDB on every request.

Important APIs and types: Public entry points include `getAcl`, `checkAccess`, `getLongestPrefixPath`, `getPrefixInfo`, `addAcl`, `removeAcl`, `setAcl`, and `getResolvedPrefixObj`. `OMPrefixAclOpResult` returns the updated `OmPrefixInfo` plus a boolean indicating whether the ACL set materially changed. It uses `OzoneObj`, `RequestContext`, `OzoneAcl`, `OmBucketInfo`, `OmPrefixInfo`, and `OzoneAclUtil`.

Control flow: Construction calls `loadPrefixTree`, iterating `prefixTable` and inserting every persisted prefix. Read paths validate that the object is a prefix, resolve link buckets through `OzoneManager.resolveBucketLink`, acquire `PREFIX_LOCK`, find the longest radix-tree match, and only return ACLs when the requested prefix exactly equals the longest prefix. Mutation helpers build or modify `OmPrefixInfo`, inherit default ACLs from the direct parent prefix or bucket when creating a new prefix, update the radix tree, and write `prefixTable` directly only when Ratis is disabled.

State and persistence behavior: Persistent state is `prefixTable`; runtime state is the radix tree. Under HA/Ratis, request/response code owns DB persistence while this class updates the in-memory tree. New prefixes may get object and update IDs derived from the OM epoch and transaction log index.

Dependencies and integration points: It integrates with OM ACL request classes, bucket-link resolution, `OzoneManagerLock.PREFIX_LOCK`, bucket metadata for default ACL inheritance, and `OmPrefixInfo` codecs in the OM DB definition.

Risks and test signals: Load failures log but leave a partial or empty tree, making startup consistency important. `EMPTY_ACL_LIST` is mutable because it is an `ArrayList`. Exact-match behavior means parent prefix ACLs are used for access only through `getLongestPrefixPath`-style callers, not `getAcl` for arbitrary descendants. Tests should cover Ratis and non-Ratis persistence, link bucket resolution, inherited default ACL conversion to access ACLs, trailing slash validation, empty ACL removal deleting the prefix, and concurrent lock discipline.
