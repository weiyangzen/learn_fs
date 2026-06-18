# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/blknum.c

Provides 64-bit block-number and group-descriptor accessor helpers. It centralizes low/high field composition for ext2/ext4 superblock counters, group descriptor block pointers, counts, flags, checksums, and inode size/ACL fields.

Major API groups:
- Group geometry: `ext2fs_group_of_blk2`, `ext2fs_group_first_block2`, `ext2fs_group_last_block2`, `ext2fs_group_blocks_count`.
- Inode block counts: `ext2fs_inode_data_blocks2`, `ext2fs_inode_i_blocks`, `ext2fs_get_stat_i_blocks`.
- Superblock counters: blocks, reserved blocks, free blocks get/set/add.
- Descriptor access: `ext2fs_group_desc` and internal `ext4fs_group_desc`.
- Group descriptor fields: bitmap locations/checksums, inode table location, free counts, used dirs, unused inode table count, flags, checksum.
- Inode fields: `ext2fs_file_acl_block`, `ext2fs_file_acl_block_set`, `ext2fs_inode_size_set`.

Behavior details:
- 64-bit high halves are only used when the filesystem has the 64bit feature.
- `ext2fs_group_desc` can index an in-memory descriptor table or lazily read a descriptor block into a static buffer if `gdp` is NULL.
- `ext2fs_inode_size_set` updates `large_file` or `largedir` features when needed, updates dynamic revision if necessary, marks the superblock dirty, and rejects oversized non-regular/non-directory files.

Implementation notes:
- The static lazy descriptor buffer in `ext2fs_group_desc` is process-global and not thread-safe.
- Several setters intentionally leave high fields untouched when 64bit is not enabled.
- `ext2fs_inode_data_blocks2` subtracts external ACL cluster sectors from `i_blocks`.
