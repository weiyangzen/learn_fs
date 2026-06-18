# File Research: sources/os/linux/linux/fs/efs/inode.c

Implements EFS inode loading and extent-based logical block mapping.

Key behavior:
- Defines address-space operations using `block_read_full_folio()` and `generic_block_bmap()`.
- `extent_copy()` converts the raw 8-byte on-disk extent into CPU-endian bitfields.
- `efs_iget()` computes the disk location of an inode from cylinder group layout, reads the dinode, fills VFS metadata, decodes device numbers, copies direct extents, and installs operations by file type.
- Regular files use `generic_ro_fops` plus EFS address-space operations.
- Symlinks use page symlink operations and EFS symlink aops.
- Special files are initialized from decoded device numbers.
- `efs_extent_check()` tests whether an extent covers a logical block.
- `efs_map_block()` maps logical blocks through direct extents or indirect extent blocks, caching the last matching extent.

Important interactions:
- Depends on superblock geometry loaded by `super.c`.
- Extent magic validation treats nonzero magic as corruption.
- The indirect extent search reads extent blocks with `sb_bread()`.
