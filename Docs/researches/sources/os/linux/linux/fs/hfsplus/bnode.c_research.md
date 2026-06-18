# File Research: sources/os/linux/linux/fs/hfsplus/bnode.c

Purpose: Implements HFS+ B-tree node page I/O, intra-node copy/move/clear, node validation/loading, hash-cache management, reference counting, unlinking, and deletion cleanup.

Key functions:
- `hfs_bnode_read()`, `hfs_bnode_write()`, `hfs_bnode_clear()`, `hfs_bnode_copy()`, and `hfs_bnode_move()` operate across one or more page-cache pages with offset/length validation.
- `hfs_bnode_read_key()` reads fixed or variable-length keys, with special handling for attributes tree keys.
- `hfs_bnode_dump()` emits debug information about node headers and offsets.
- `hfs_bnode_unlink()` relinks siblings, updates tree leaf head/tail/root/depth, and marks the node deleted.
- `hfs_bnode_findhash()`, `hfs_bnode_unhash()`, `hfs_bnode_find()`, and `hfs_bnode_create()` maintain the node hash cache and load/create node pages.
- `hfs_bnode_put()` decrements refs, frees deleted nodes, zeroes nodes when required, and returns node IDs to the B-tree bitmap.
- `hfs_bnode_need_zeroout()` checks the volume attribute requesting unused catalog nodes be zeroed.

Dependencies and integration:
- Used by all HFS+ B-tree search and mutation code.
- Relies on validation helpers such as `is_bnode_offset_valid()` and `check_and_correct_requested_length()` from HFS+ headers/common code.
- Interacts with `hfs_bmap_free()` from `btree.c`.

Risk notes:
- Node validation checks type, height, record offsets, entry sizes, and key sizes, reducing malformed-tree exposure.
- Refcount/hash locking correctness is critical because B-tree pages may be reclaimed through address-space operations elsewhere.
