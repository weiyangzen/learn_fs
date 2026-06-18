# File Research: sources/os/linux/linux-stable/fs/befs/inode.h

This small header declares the BeFS inode validation API.

Export:
- `befs_check_inode(struct super_block *sb, befs_inode *raw_inode, befs_blocknr_t inode)`

Integration:
- Included by `linuxvfs.c`.
- Implemented in `inode.c`.

Risk notes:
- The header has no include guard, but it only contains one prototype and is used narrowly.
