# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_olt.h

Read status: complete, 120 lines.

Purpose: defines VxFS Object Location Table headers and record formats.

Key content:
- Defines `VXFS_OLT_MAGIC`.
- Enumerates OLT record types: free, fileset header, current usage table, inode list, device, and superblock/log/OLT inode records.
- `struct vxfs_olt` models the OLT extent header.
- Defines common/free/ilist/cut/sb/dev/fshead record structures.

Used by: `vxfs_olt.c` to find the fileset header inode and initial inode-list extent.
