# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_inode.h

Read status: complete, 169 lines.

Purpose: defines VxFS on-disk and in-memory inode structures plus extent descriptor formats.

Key content:
- Constants for disk inode size, direct/indirect extent counts, immediate data size, typed extent count, and typed extent header masks.
- Typed extent descriptor types include indirect/data and DEV4 variants.
- `struct vxfs_dinode` models on-disk inode metadata, timestamps, type/organization, rdev/dotdot/regular/vxspec union, block count, generation, version, and organization-specific data.
- `struct vxfs_inode_info` embeds `struct inode` and stores converted VxFS metadata plus raw organization data.
- `VXFS_INO()` maps a VFS inode to its containing FreeVxFS inode.

Used by: almost every FreeVxFS implementation file.
