# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/util/RadixTree.java

Purpose: In-memory radix/prefix tree for Ozone slash-delimited prefix path lookup, used primarily by ACL APIs.

Important APIs and types: Root `RadixNode`, `isEmpty`, `insert`, `getLastNodeInPrefixPath`, `removePrefixPath`, `getLongestPrefixPath`, `radixPathToString`, and `getLongestPrefix`.

Control flow: `insert` normalizes input with `Paths.get`, walks each path component, creates missing child nodes, and optionally stores a value on the terminal node. Exact lookup compares longest-prefix length to path name count plus root. Removal recursively deletes the non-overlapping suffix when a removed node has no children. Longest-prefix methods traverse until a missing component or leaf is hit and return either nodes or a string path.

State and persistence behavior: Pure in-memory tree. No persistence or synchronization. Root is named `/` and may hold a value if extended later.

Dependencies and integration points: Used by ACL prefix matching code to find exact or longest prefix ACL metadata. Uses `OzoneConsts.OZONE_URI_DELIMITER` and Java NIO `Path`.

Risks: Because `RadixNode.hasChildren` is inverted, removal and empty checks are easy to misread. Java `Paths.get` behavior is platform-sensitive for separators and path normalization; Ozone paths assume `/`. Raw node/map types reduce generic safety. No concurrency protection is provided.

Test signals: Insert exact paths, longest-prefix lookup, root-only empty state, removal of leaf and overlapping prefixes, trailing slash rendering, value retrieval, and platform-independent slash behavior.
