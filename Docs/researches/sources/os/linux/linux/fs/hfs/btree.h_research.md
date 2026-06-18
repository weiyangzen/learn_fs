# File Research: sources/os/linux/linux/fs/hfs/btree.h

Purpose: Defines the in-memory HFS B-tree and B-node data structures, search cursor state, lock classes, flags, and public B-tree helper prototypes.

Key structures:
- `struct hfs_btree` stores superblock, backing inode, comparator, catalog/extents CNID, tree header fields, node size/depth, mutex, and node hash table.
- `struct hfs_bnode` stores node identity, sibling/parent links, type/height, record count, refcount, flags, wait queue, page offset, and variable page array.
- `struct hfs_find_data` carries search and current keys, target tree, current node, record index, and key/entry offsets and lengths.

Dependencies and integration:
- Includes `hfs_fs.h`, so all HFS B-tree users share the filesystem-private inode/superblock definitions.
- Exposes APIs implemented across `btree.c`, `bnode.c`, `brec.c`, and `bfind.c`.

Risk notes:
- This header is central to cross-file invariants: callers must hold `tree_lock` via `hfs_find_init()` while mutating records and must balance `hfs_bnode_get()`/`hfs_bnode_put()`.
