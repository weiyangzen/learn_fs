# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_fshead.c

This file reads VxFS fileset headers and establishes the inode-list inodes needed for normal inode lookup.

Major responsibilities:
- Read the fileset header inode from the initial inode-list extent discovered via the OLT.
- Validate that the fileset header inode has the VxFS fileset-header type.
- Read the structural and primary fileset headers from that inode.
- Locate and validate the structural inode list inode.
- Locate and validate the primary inode list inode.
- Store the resulting inode pointers in `vxfs_sb_info`.

Important design points:
- Fileset headers are read through `vxfs_bread()` from a fake fileset header inode.
- The driver copies on-disk header bytes into allocated memory, uses the needed fields, and frees the copies after setup.
- Structural metadata is read first so that ordinary inode-list lookup can proceed through `vxfs_stiget()`.
- Errors unwind all acquired inodes and allocated fileset header buffers.

Key invariants:
- `vsi_fship` must decode as `VXFS_IFFSH`.
- `vsi_stilist` and `vsi_ilist` must decode as `VXFS_IFILT`.
- Fileset header fields must be byte-swapped through `fs32_to_cpu()`.
- Successful mount setup requires both structural and primary inode list inodes.

External interfaces:
- Provides `vxfs_read_fshead()` for `vxfs_fill_super()`.
