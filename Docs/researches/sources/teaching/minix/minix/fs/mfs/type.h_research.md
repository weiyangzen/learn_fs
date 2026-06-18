# File Research: sources/teaching/minix/minix/fs/mfs/type.h

`type.h` defines `d2_inode`, the on-disk V2/V3-style disk inode structure used by MFS. It contains mode, link count, uid, gid, size, atime, mtime, ctime, and `V2_NR_TZONES` zone pointers.

The type is used by `buf.h` buffer overlays and by `inode.c`'s `new_icopy` routine to copy between disk inodes and in-core `struct inode` objects with possible byte-order conversion.
