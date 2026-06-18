# File Research: sources/os/linux/linux-stable/fs/hfs/btree.c

## Scope

Opens, closes, writes, grows, and allocates/free nodes for classic HFS catalog and extents B-trees.

## APIs And Behavior

- `hfs_btree_open()` allocates an in-memory `hfs_btree`, creates/initializes the special CNID inode, reads the on-disk header node into page cache, validates node size/count and max key length, and installs `hfs_btree_aops`.
- `hfs_btree_close()` releases all cached bnodes, warns about nonzero bnode refs, drops the tree inode, and frees the tree.
- `hfs_btree_write()` updates the header record fields for root, leaf count/head/tail, node count/free count, attributes, and depth.
- `hfs_bmap_reserve()` extends the tree file until enough free B-tree nodes exist, then updates inode sizes and tree node counts.
- `hfs_bmap_alloc()` scans the header/map-node bitmap for a free node bit, marks it allocated, creates map nodes when needed, decrements `free_nodes`, and returns a zeroed bnode via `hfs_bnode_create()`.
- `hfs_bmap_free()` locates the map bit for a node, clears it, and increments `free_nodes`.

## State And Dependencies

This file bridges the HFS MDB fork records to in-memory B-tree metadata. It depends on `hfs_inode_read_fork()`, `hfs_ext_find_block()`, special CNIDs `HFS_EXT_CNID` and `HFS_CAT_CNID`, page-cache helpers, block reads, and bnode primitives.

## Risks And Invariants

Tree header validation is limited but important: node size must be a power of two, node count nonzero, and max key length must match the requested tree type. Bmap allocation assumes `hfs_bmap_reserve()` has made enough nodes available. Map-node creation still contains panic/FIXME behavior if `free_nodes` is unexpectedly zero.
