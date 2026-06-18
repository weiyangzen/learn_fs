# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/i_block.c

## Role

Maintains inode `i_blocks` accounting across normal and huge-file ext4 modes.

## Main Flow

- `ext2fs_iblk_add_blocks()` adds filesystem blocks/clusters to inode sector/block accounting.
- `ext2fs_iblk_sub_blocks()` subtracts with underflow detection.
- `ext2fs_iblk_set()` sets the accounting field directly.
- For non-huge-file representation, counts are converted to 512-byte sectors; for `EXT4_HUGE_FILE_FL`, block units are used.

## Dependencies

Uses superblock huge-file feature checks and `EXT2FS_CLUSTER_RATIO(fs)`.

## Risks / Notes

- Returns `EOVERFLOW` if the 32-bit low field would overflow without huge-file support.
- Cluster ratio multiplication means callers must pass counts in logical filesystem blocks, not already-scaled sectors.
