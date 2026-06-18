# File Research: sources/os/linux/linux-stable/fs/efs/efs.h

## Summary
Defines EFS in-memory and on-disk structures, constants, helpers, and cross-file declarations.

## Main Contents
- 512-byte block constants.
- On-disk extent, inode, device, directory entry, and directory block layouts.
- `struct efs_inode_info`.
- Conversion helpers `INODE_INFO()` and `SUPER_INFO()`.
- Function declarations for inode, block mapping, lookup, export, and bmap operations.

## Important Details
EFS uses up to 12 direct extents stored in the inode and indirect extent blocks for larger files. Directory entries are slot-offset based inside fixed-size directory blocks.

## Risks
Bitfield and packed on-disk extent interpretation must remain consistent with IRIX EFS layout assumptions.
