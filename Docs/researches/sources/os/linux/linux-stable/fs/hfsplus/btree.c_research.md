# File Research: sources/os/linux/linux-stable/fs/hfsplus/btree.c

## Scope

Opens/closes/writes HFS+ B-trees, computes metadata-file clump sizes, manages B-tree node bitmap records, reserves/allocates/frees B-tree nodes, and validates map state.

## APIs And Behavior

- `hfsplus_calc_btree_clump_size()` computes default clump sizes for catalog, attributes, and extents trees based on volume size and node/block size.
- `hfs_btree_open()` loads a special-file inode, reads the header record, validates max key length, flags, node size/count, and installs the correct comparator for extents/catalog/attributes. It also checks bit 0 in the tree map and forces read-only on corruption.
- `hfs_btree_close()` releases cached nodes and the tree inode.
- `hfs_btree_write()` writes root, leaf, node count/free count, attributes, and depth back to the header node.
- `hfs_bmap_reserve()` extends the tree file until enough free nodes are available, optionally zeroing newly allocated bnodes for catalog unused-node fix.
- `hfs_bmap_alloc()` scans header/map-node bitmap records for a free node bit, creates new map nodes if needed, writes the header, and returns a new bnode.
- `hfs_bmap_free()` locates and clears a node bit through validated map-record access and updates free-node counts.

## State And Dependencies

This file depends on special CNID inodes via `hfsplus_iget()`, bnode loading/validation, extent-backed file extension, catalog/casefold flags, HFSX key type, and volume header attributes. It relies on `tree_lock` being held for bmap reserve/alloc/free.

## Risks And Invariants

Catalog trees require variable index keys; extents trees reject variable index keys; all HFS+ B-trees require big keys. Header/map-node bitmap access validates node type and record offsets before mapping pages. Detected map corruption forces the superblock read-only rather than failing mount outright.
