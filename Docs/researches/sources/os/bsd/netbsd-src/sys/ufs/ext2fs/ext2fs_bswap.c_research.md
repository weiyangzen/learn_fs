# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_bswap.c

This file provides byte-swapping support for ext2fs on big-endian systems. It is compiled as meaningful code only when `BYTE_ORDER == BIG_ENDIAN`.

Key functions:
- `e2fs_sb_bswap`: swaps selected superblock fields between disk little-endian and host order, preserving unused fields by first copying the full structure.
- `e2fs_i_bswap`: swaps inode fields for a given on-disk inode size, including ext4 extra inode fields only when they fit.

Dependencies:
- `sys/endian.h`, `ext2fs.h`, `ext2fs_dinode.h`.
- Kernel `systm.h` or userland `string.h`.

Important behavior:
- Little-endian builds use macros in headers that reduce load/save operations to `memcpy`; this file only matters on big-endian.
- Inode swapping respects `EXT2_REV0_DINODE_SIZE` and `EXT2_DINODE_FITS` to avoid touching fields not present in older/smaller inodes.

Design notes:
- Not every modern superblock field is explicitly swapped; preserved fields remain copied as-is unless listed.
