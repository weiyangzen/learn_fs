# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_fshead.c

Read status: complete, 166 lines.

Purpose: reads VxFS fileset headers and initializes inode-list inodes needed for normal inode lookup.

Key flow:
- `vxfs_getfsh()` reads a fileset header block through `vxfs_bread()`, copies it into kmalloc memory, and releases the buffer.
- `vxfs_read_fshead()` reads the fileset header inode using OLT-derived `vsi_iext` and `vsi_fshino`.
- Validates the fileset header inode is `VXFS_IFFSH`.
- Reads structural and primary fileset headers.
- Reads and validates the structural inode list and primary inode list as `VXFS_IFILT`.
- Stores `vsi_fship`, `vsi_stilist`, and `vsi_ilist` in superblock-private state.

Important dependencies: `vxfs_blkiget`, `vxfs_stiget`, `vxfs_bread`, `vxfs_fsh`, inode type predicates.

Failure handling: releases partially acquired inodes and allocated header copies before returning `-EINVAL`.
