# File Research: sources/os/linux/linux-stable/fs/qnx4/qnx4.h

## Summary
Private header for QNX4 filesystem implementation.

## Main Responsibilities
- Define QNX4 superblock and inode wrapper structures.
- Declare inode, lookup, bitmap, block-map, and directory operation interfaces.
- Provide accessors for `qnx4_sb_info`, `qnx4_inode_info`, and raw inode data.
- Define `union qnx4_directory_entry` to safely inspect inode and link directory entries.
- Provide `get_entry_fname()` for directory entry validation/name extraction.

## Important Behavior
The directory-entry union uses a fixed 48-byte `de_name` array to avoid compiler confusion over different union member name-array sizes. Compile-time assertions ensure the status byte is at the same offset in all relevant structures.

## Cross-File Interactions
Included by all QNX4 implementation files and backed by UAPI on-disk structure definitions in `include/uapi/linux/qnx4_fs.h`.
