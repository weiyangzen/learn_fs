# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_bmap.c

Implements VOP block mapping for ext2fs. `ext2fs_bmap` returns the underlying device vnode when requested, then maps logical to physical blocks through either ext4 extents or classic direct/indirect block arrays depending on the inode `EXT4_EXTENTS` flag.

`ext4_bmapext` finds the covering extent and computes the physical block. `ext2fs_bmaparray` uses `ufs_getlbns`, direct inode block pointers, and indirect block traversal to resolve disk addresses; it reads indirect blocks as needed, recognizes cache-resident metadata, returns `-1` for holes, and computes sequential run length for clustering.
