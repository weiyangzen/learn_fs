# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_dinode.h

This header defines the ext2/ext3/ext4 on-disk inode format and inode-related constants/macros.

Key definitions:
- Reserved inode numbers: bad blocks, root, ACL, bootloader, undelete, resize, journal, first normal inode.
- `EXT2FS_NDADDR` and `EXT2FS_NIADDR`, matching UFS direct/indirect address counts.
- `struct ext2fs_dinode`: on-disk inode fields including mode, uid/gid, size, times, link count, block count, flags, block pointer array, generation, ACL, high size/block fields, checksums, extra inode size, nanosecond/epoch time fields, birth time, version high, and project id.
- `i_e2fs_*` macros mapping NetBSD in-memory inode fields to ext2 dinode members.
- Ext2 permission, file type, and file flag constants.
- Inode size helpers: `EXT2_DINODE_SIZE`, `EXT2_DINODE_FITS`.
- Time helpers: `ext2fs_dinode_time_get`, `EXT2_DINODE_TIME_GET`, `ext2fs_dinode_time_set`, `EXT2_DINODE_TIME_SET`.
- Overlay macros for device numbers and short symlinks.
- Endian load/save macros and big-endian byte-swap declaration.

Dependencies:
- `sys/stat.h`.
- `stddef.h` outside kernel/standalone for `offsetof`.

Design notes:
- Extra timestamp fields encode nanoseconds plus high epoch bits. The getter preserves Linux compatibility behavior for the `epoch_bits == 3` negative-time case.
- Short symlink data overlays the block pointer array.
