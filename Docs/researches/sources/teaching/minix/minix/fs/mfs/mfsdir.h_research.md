# File Research: sources/teaching/minix/minix/fs/mfs/mfsdir.h

`mfsdir.h` defines the MFS on-disk directory entry format. `MFS_DIRSIZ` is fixed at 60 bytes and cannot change without breaking existing filesystems, because MFS stores names directly in `struct direct`.

`struct direct` is packed and contains a 32-bit inode number (`mfs_d_ino`) plus a fixed-size filename array (`mfs_d_name`). Directory traversal and mutation in `path.c` cast directory blocks to arrays of this structure through `b_dir`.
