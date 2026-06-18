# File Research: sources/local-fs/jfsutils/include/jfs_btree.h

Common JFS B+-tree page definitions used by directory trees and extent trees.

Key contents:
- Defines `struct btpage`, a 4096-byte generic B+-tree page with sibling links, flags, self address, and 4064-byte type-specific entry area.
- Defines flags: root, leaf, internal, rightmost, leftmost, type mask, and endian-swapped marker.

Interactions:
- Included by `jfs_dtree.h` and `jfs_xtree.h`.

Research notes:
- Compact shared on-disk page shape; higher-level headers define typed interpretations.
