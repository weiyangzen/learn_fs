# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_dir.h

Read status: complete, 68 lines.

Purpose: defines VxFS on-disk directory block and directory entry structures.

Key content:
- `struct vxfs_dirblk` contains free-space and hash-chain metadata at the start of each directory block.
- `VXFS_NAMELEN` is 256.
- `struct vxfs_direct` stores inode number, record length, name length, hash-next pointer, and name bytes.
- Directory entry alignment helpers define 4-byte padding, minimum record size, rounded length, and per-block overhead.

Used by: `vxfs_lookup.c` for directory scanning and `vxfs_super.c` for statfs name length.
