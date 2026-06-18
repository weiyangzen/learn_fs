# File Research: sources/os/linux/linux/fs/hfsplus/btree.c

Purpose: Opens, validates, writes, grows, allocates, and frees HFS+ B-tree nodes for extents, catalog, and attributes trees.

Key functions:
- `hfsplus_calc_btree_clump_size()` computes B-tree clump sizes from volume size, node size, block size, and tree type.
- `hfs_btree_open()` reads tree header data, validates max-key lengths/flags/node counts, selects comparators, and verifies map bit 0.
- `hfs_btree_close()` releases cached nodes and backing inode.
- `hfs_btree_write()` writes updated header counters.
- `hfs_bmap_reserve()` extends the B-tree file to reserve free nodes.
- `hfs_bmap_alloc()` scans header/map node bitmap records, sets a free bit, writes header metadata, and creates the node.
- `hfs_bmap_free()` clears a node allocation bit through validated map-record helpers.

Dependencies and integration:
- Uses `hfsplus_iget()` to load special B-tree inodes.
- Comparator selection depends on HFSX and catalog key type.
- Calls `hfsplus_file_extend()` from `extents.c` and zeroes new catalog nodes when volume attributes require it.

Risk notes:
- If header map bit 0 is invalid, the filesystem is forced read-only and fsck is recommended.
- Uses lockdep assertions to require tree mutex ownership for bitmap reserve/alloc/free.
