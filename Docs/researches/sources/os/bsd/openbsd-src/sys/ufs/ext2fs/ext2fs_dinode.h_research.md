# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_dinode.h

Defines ext2 on-disk inode layout and inode constants. Reserved inode numbers include root inode 2, resize inode 7, and first normal inode 11. `NDADDR` is 12 and `NIADDR` is 3, matching the classic direct/single/double/triple indirect pointer layout.

`struct ext2fs_dinode` contains mode, uid/gid low/high, size low/high, timestamps, deletion time, link count, block count, flags, version, block pointers, generation, ACL fields, checksum fields, extra inode size, extra timestamps, creation time, and high version bits. Macros define ext2 mode bits, file types, inode flags such as immutable/append/extents/huge-file, inode size selection, device/short-symlink overlays, and endian load/save helpers.
