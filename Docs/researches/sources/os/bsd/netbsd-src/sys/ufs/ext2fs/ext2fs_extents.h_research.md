# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_extents.h

This header defines ext4 extent structures and lookup APIs used by NetBSD ext2fs.

Key definitions:
- `EXT4_EXT_MAGIC`
- Extent cache result types: no hit, sparse gap, in extent.
- `struct ext4_extent`: leaf extent with logical start, length, and high/low physical start.
- `struct ext4_extent_index`: interior-tree entry pointing to a lower-level block.
- `struct ext4_extent_header`: tree header with magic, entry count, capacity, depth, and generation.
- `struct ext4_extent_cache`: cached logical-to-physical extent or gap.
- `struct ext4_extent_path`: traversal result/path object holding depth, buffer, sparse state, selected extent/index/header.

Public prototypes:
- `ext4_ext_in_cache`
- `ext4_ext_put_cache`
- `ext4_ext_find_extent`

Dependencies:
- `ufs/ufs/inode.h`, `sys/types.h`, and `stdbool.h` outside kernel.
- Forward declarations for `struct inode` and `struct m_ext2fs`.

Design notes:
- Structures mirror ext4 disk format but are used here for read-side lookup.
