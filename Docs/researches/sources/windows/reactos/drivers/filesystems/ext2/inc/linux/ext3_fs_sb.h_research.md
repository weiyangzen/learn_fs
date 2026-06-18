# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext3_fs_sb.h

This header defines the in-memory ext3 superblock information used by the driver.

Key structures:
- `struct ext3_gd`: group descriptor cache entry with block number, `ext4_group_desc` pointer, and backing `buffer_head`.
- `struct ext3_sb_info`: group descriptor lock/cache, descriptor sizing, group/inode/block geometry, address/descriptor bit counts, raw superblock pointer, first inode, htree hash seed, and default hash version.

Role:
- Provides the `s_fs_info` payload behind `EXT3_SB(sb)` and `EXT4_SB(sb)`.
- Used by group descriptor lookup, inode/block bitmap initialization, htree hashing, and superblock feature checks.

Declared function:
- `ext3_release_dir(struct inode *inode, struct file *filp)`.
