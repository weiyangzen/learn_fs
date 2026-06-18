# File Research: sources/os/linux/linux/fs/qnx4/inode.c

## Role

Main QNX4 filesystem implementation: superblock mount, block mapping, inode loading, statfs, address-space operations, inode cache, and filesystem registration.

## Mount and Superblock

- Always forces `SB_RDONLY`.
- `qnx4_fill_super()` allocates `qnx4_sb_info`, sets 512-byte block size, reads block 1 superblock, checks root directory, locates `.bitmap`, loads root inode, and creates root dentry.
- `qnx4_checkroot()` verifies the root directory name and scans root extents for `.bitmap`.
- `qnx4_kill_sb()` frees copied bitmap inode and private superblock info.

## Block Mapping

- `qnx4_block_map()` maps file logical blocks:
  - first checks the inode's first extent;
  - follows chained extent blocks via `di_xblk`;
  - validates extent block signature `"IamXblk"`;
  - returns physical block numbers adjusted from QNX's 1-based block numbering.
- `qnx4_get_block()` adapts block mapping for buffer/page-cache helpers.

## Inodes

- `qnx4_iget()` reads raw inode entries from inode blocks, converts mode/uid/gid/link count/size/timestamps, copies the raw 64-byte inode entry into private inode state, and installs operations for regular files, directories, or symlinks.
- Regular files use `generic_ro_fops` and qnx4 address-space operations.
- Symlinks use page symlink operations.
- Unexpected inode modes fail with `-EIO`.

## Other Operations

- `qnx4_statfs()` reports block counts from bitmap size and free blocks from bitmap scan.
- `qnx4_read_folio()` and `qnx4_bmap()` use generic block helpers.
- Registers filesystem type `qnx4` and a slab cache for private inode info.

## Research Notes

The driver is intentionally read-only but still performs raw extent-chain parsing. Error handling is mostly conservative: malformed roots, unreadable inodes, invalid extent blocks, or unsupported inode types abort operations.
