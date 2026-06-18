# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_bmap.c

This file implements VOP_BMAP support, converting file logical block numbers to device block numbers.

Key functions:
- `ext2fs_bmap`: VOP entry point. Returns the underlying device vnode and dispatches to extent or classic block-pointer mapping.
- `ext4_bmapext`: maps logical blocks through ext4 extents using `ext4_ext_find_extent`.
- `ext2fs_bmaparray`: maps logical blocks through direct and indirect ext2 block pointers.

Important behavior:
- If the inode has `EXT2_EXTENTS`, mapping uses the extents path.
- Sparse or unmapped blocks return `-1` in `a_bnp`.
- Direct block mapping can compute sequential run length for clustering.
- Indirect mapping uses `ufs_getlbns`, checks cached indirect buffers with `incore`, reads missing indirect buffers through strategy I/O, and can compute run length within the final indirect block.
- Indirect metadata logical block numbers follow UFS negative-lbn conventions.

Dependencies:
- UFS inode/mount helpers and `blkptrtodb`.
- Ext2fs extent lookup from `ext2fs_extents.c`.
- Buffer cache and vnode strategy I/O APIs.

Design notes:
- This is mapping-only; it does not allocate blocks.
- Extent mapping sets `runp` and optional `runb` based on extent length or sparse range.
