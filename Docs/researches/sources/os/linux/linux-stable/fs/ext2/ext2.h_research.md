# File Research: sources/os/linux/linux-stable/fs/ext2/ext2.h

## Summary
Central ext2 private header defining in-memory structures, on-disk structures, feature flags, mount flags, allocation constants, directory formats, helper macros, and cross-file prototypes.

## Main Contents
- Block number typedefs and reservation-window structures.
- `struct ext2_sb_info` with group geometry, superblock buffers, counters, locks, reservation tree, xattr cache, and DAX state.
- `struct ext2_inode_info` with block pointers, flags, xattr fields, block group, reservation info, lookup hint, locks, orphan/quota state, and VFS inode.
- On-disk `struct ext2_super_block`, `struct ext2_inode`, and directory entry formats.
- Feature flags for compat, ro-compat, and incompat ext2/ext3-era features.
- Mount option flags and ioctl constants.
- Prototypes for block allocation, inode allocation, directory helpers, inode mapping, ioctl, namei, superblock, and operation tables.

## Important Behavior
The header defines the supported feature masks, including support for ext attrs, filetype, meta_bg, sparse super, large file, and btree dir. It maps ext2 file flags to VFS inode flags through declarations implemented in `inode.c`.

Inline helpers compute first/last block of a group and wrap little-endian bitmap bit operations.

## Risks
Many ext2 subsystems share mutable state declared here: blockgroup locks, reservation tree locks, inode metadata locks, truncate mutexes, and percpu counters. Misusing these interfaces can desynchronize disk metadata and in-memory accounting.
