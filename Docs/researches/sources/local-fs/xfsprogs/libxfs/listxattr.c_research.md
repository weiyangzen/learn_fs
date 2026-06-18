# File Research: sources/local-fs/xfsprogs/libxfs/listxattr.c

Walks all extended attributes of an XFS inode and calls a callback for each entry.

Key responsibilities:
- Handles shortform, leaf-format, and node-format attr forks.
- Extracts local values directly and reports remote values as name plus length with NULL value pointer.
- Loads attr fork extents before walking non-local attrs.
- Traverses attr dabtree nodes to the leftmost leaf, then follows leaf sibling links.
- Uses a bitmap loop detector for node/leaf traversal.

Important behavior:
- Shortform attrs are walked from in-core fork data.
- Leaf entries report namespace flags, name, namelen, value pointer, and valuelen.
- Node walk verifies node magic, level progression, nonzero count, and repeated-block avoidance.
- Remote attr consumers must fetch values separately.

Dependencies:
- Uses libxfs attr leaf/node readers, attr fork extent loading, bitmap helpers, transactions, and inode attr helpers.

Notable risks:
- Corrupt dabtrees return `EFSCORRUPTED`; callbacks must preserve traversal invariants.
- A commented-out `xfs_failaddr_t` hints verifier-style diagnostics are not used here.
