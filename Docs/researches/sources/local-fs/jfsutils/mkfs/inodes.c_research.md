# File Research: sources/local-fs/jfsutils/mkfs/inodes.c

Initializes initial aggregate and fileset inodes for a newly formatted JFS filesystem.

Key functions:
- `init_aggr_inode_table(...)`: writes the first aggregate inode extent, initializes aggregate self inode, inline log inode, and bad-block inode, swaps inode endianness for disk, and marks inode-table blocks allocated.
- `init_fileset_inode_table(...)`: writes first fileset inode extent, including reserved inode, extension/superblock-reserved inode, root directory inode, and ACL inode.
- `init_fileset_inodes(...)`: writes the aggregate fileset inode that points to the fileset inode map.
- `init_inode(...)`: common initializer for dinode fields and inline/extent/no-data data roots.

Root directory initialization:
- Creates a directory B+tree root in the root inode’s DASD area.
- Sets `DXD_INDEX | BT_ROOT | BT_LEAF`.
- Initializes root free slot chain, `idotdot`, link count, and directory free counters.

Extent inode initialization:
- Creates an inline xtree root with an initial XAD when data exists.
- For `no_data`, creates an empty xtree root with `nextindex = XTENTRYSTART`.

Filesystem relevance: lays down the minimal inode set required for a valid JFS aggregate and its initial fileset.
