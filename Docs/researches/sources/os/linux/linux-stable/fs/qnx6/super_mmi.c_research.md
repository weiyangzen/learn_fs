# File Research: sources/os/linux/linux-stable/fs/qnx6/super_mmi.c

## Summary
Implements QNX6 MMI filesystem superblock handling.

## Main Responsibilities
- Read and validate two MMI superblocks.
- Verify magic and CRC32 checksums.
- Switch to the on-disk block size after the first superblock read.
- Convert MMI superblock layout into the standard `qnx6_super_block` layout.
- Select the active superblock by serial number.
- Set QNX6 block offset for MMI layout.

## Key Interfaces
- `qnx6_mmi_fill_super()` is called by `qnx6_fill_super()` when the `mmi_fs` mount option is set.

## Important Behavior
The second MMI superblock is located using `sb_num_blocks + QNX6_SUPERBLOCK_AREA / blocksize`. After selecting the active copy, the code copies the MMI fields into a standard QNX6 superblock structure, writes that structure into the selected buffer, and stores it in `sbi->sb`.

## Cross-File Interactions
Uses endian helpers and debug hooks from `qnx6.h`; returns the active superblock to `inode.c` mount setup.
