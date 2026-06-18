# File Research: sources/os/linux/linux/fs/qnx6/super_mmi.c

## Role

Handles the QNX6 `mmi_fs` superblock variant.

## Key Functions

- `qnx6_mmi_copy_sb()` copies fields from an MMI superblock layout into the normal `qnx6_super_block` layout, including root nodes for inode, bitmap, and longfile metadata.
- `qnx6_mmi_fill_super()`:
  - reads the first MMI superblock at block 0;
  - validates magic and CRC32 checksum;
  - switches to the on-disk block size;
  - reads the second superblock;
  - validates magic and checksum;
  - chooses the active superblock by serial number;
  - copies the chosen MMI superblock into a normal-layout buffer;
  - sets `sbi->sb_buf`, `sbi->sb`, and `s_blks_off`.

## Research Notes

This adapter lets the main QNX6 mount path consume MMI superblocks as if they were normal QNX6 superblocks after conversion.
