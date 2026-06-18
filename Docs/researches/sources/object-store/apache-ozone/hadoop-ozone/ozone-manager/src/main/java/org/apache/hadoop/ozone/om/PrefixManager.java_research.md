# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/PrefixManager.java

Purpose: `PrefixManager` defines the OM service contract for prefix ACL management and lookup. It extends `IOzoneAcl`, so prefix objects can participate in the same ACL read/check APIs used by volumes, buckets, and keys.

Important APIs and types: It exposes `getMetadataManager()` and `getLongestPrefixPath(String path)`. Implementations return `OmPrefixInfo` values representing the prefix nodes along the longest matching path and inherit `getAcl` and `checkAccess` from `IOzoneAcl`.

Control flow: The interface does not implement flow. `PrefixManagerImpl` supplies the real behavior by validating `OzoneObj` values, resolving bucket links, traversing a radix tree, and consulting OM metadata.

State and persistence behavior: The interface holds no state. Implementations are expected to read and write `prefixTable` entries and maintain an in-memory prefix index for efficient ACL checks.

Dependencies and integration points: It depends on `OMMetadataManager`, `OmPrefixInfo`, and the OM ACL subsystem. Prefix ACL request handlers use this contract to add, remove, set, list, and evaluate ACLs.

Risks and test signals: API risk is ambiguity around path normalization and trailing slash requirements, which the implementation enforces. Tests should cover longest-prefix lookup, empty path behavior, invalid resource types, and inheritance from parent prefixes or buckets.
