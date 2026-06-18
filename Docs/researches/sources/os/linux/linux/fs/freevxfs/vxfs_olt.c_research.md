# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_olt.c

Read status: complete, 105 lines.

Purpose: reads the VxFS Object Location Table to discover core metadata locations.

Key flow:
- `vxfs_oblock()` converts an on-disk block number at filesystem block size to the current superblock block units.
- `vxfs_read_olt()` reads the OLT extent, validates `VXFS_OLT_MAGIC`, rejects multi-block OLT extents, then walks OLT records.
- Recognizes `VXFS_OLT_FSHEAD` to set `vsi_fshino` and `VXFS_OLT_ILIST` to set `vsi_iext`.
- Returns success only if both fileset header inode and initial inode-list extent were found.

Important dependencies: superblock-private OLT location/size from `vxfs_super.c`, OLT structure definitions, endian helpers.

Risk note: only single-block OLT extents are supported.
