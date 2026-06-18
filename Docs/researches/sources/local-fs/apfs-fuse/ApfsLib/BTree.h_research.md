# File Research: sources/local-fs/apfs-fuse/ApfsLib/BTree.h

This header defines the APFS B-tree reader types: `BTreeEntry`, abstract `BTreeNode`, `BTreeNodeFix`, `BTreeNodeVar`, `BTree`, and `BTreeIterator`.

`BTCompareFunc` defines the comparator contract: compare search key to entry key and return -1, 0, or 1. `CompareStdKey()` is declared as a generic uint64 comparator.

`BTreeEntry` is non-copyable and stores key/value pointers plus lengths. `BTreeNode` owns a block buffer and exposes APFS node metadata. `BTree` owns the root, tree info, optional OMAP mapper, optional volume pointer, OID/XID, debug flag, and an optional mutex-protected node cache.

`BTreeIterator` tracks current node/index and can advance across leaf nodes by walking parent links and descending to the next leaf.

The header enables `BTREE_USE_MAP` by default and sets the cache target to 8192 nodes, documented as roughly 32 MB for 4 KiB nodes.
