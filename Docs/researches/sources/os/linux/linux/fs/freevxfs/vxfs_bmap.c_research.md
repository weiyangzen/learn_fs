# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_bmap.c

Read status: complete, 271 lines.

Purpose: maps VxFS logical file blocks to physical disk blocks for internal reads and page-cache block mapping.

Key flow:
- `vxfs_bmap_ext4()` handles ext4-style VxFS inode organizations: scans direct extents, then tries indirect extents.
- `vxfs_bmap_indir()` recursively walks typed indirect extent blocks and resolves typed data extents.
- `vxfs_bmap_typed()` scans the inode's inline typed extent descriptors and recurses or resolves data extents.
- `vxfs_bmap1()` dispatches by inode organization: `EXT4` and `TYPED` supported; `NONE` and `IMMED` return unsupported; unknown orgtypes warn and BUG.

Important dependencies: `sb_bread()`, buffer heads, `vxfs_inode_info`, endian helpers, typed extent format.

Risk notes:
- DEV4 typed extents are detected but unsupported.
- Unknown typed extent headers call `BUG()`, so malformed media can trigger hard failure paths.
- The ext4-style indirect calculation is subtle and appears sensitive to on-disk `indsize` correctness.
