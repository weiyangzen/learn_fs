# File Research: sources/os/linux/linux/fs/hfs/btree.c

Purpose: Opens, closes, writes, extends, allocates, and frees nodes in classic HFS B-trees.

Key functions:
- `hfs_btree_open()` creates an in-memory `hfs_btree`, attaches the extents or catalog special inode, reads node 0, validates header fields, and configures node sizing.
- `hfs_btree_close()` drains the node hash and releases the B-tree inode.
- `hfs_btree_write()` writes updated root/leaf/node/free-count metadata into the header record.
- `hfs_bmap_reserve()` extends the B-tree file until at least a requested number of free nodes exists.
- `hfs_bmap_alloc()` scans header/map-node bitmap records for a free node bit, sets it, and returns a zeroed node object.
- `hfs_bmap_free()` clears a node bit in the B-tree bitmap and increments `free_nodes`.

Dependencies and integration:
- Uses MDB fork extents from `HFS_SB(sb)->mdb` and `hfs_inode_read_fork()` to model catalog/extents B-tree files.
- Uses `hfs_ext_find_block()` to locate physical blocks for the header read.
- Works with `bnode.c` helpers declared in `btree.h` and B-tree mutation logic in `brec.c`.

Risk notes:
- Header validation covers power-of-two node size, nonzero node count, and expected max-key lengths, but assumes node 0 can be read into the first folio.
- `hfs_bmap_new_bmap()` still has a `panic("FIXME!!!")` when no free nodes remain while creating a new bitmap node.
