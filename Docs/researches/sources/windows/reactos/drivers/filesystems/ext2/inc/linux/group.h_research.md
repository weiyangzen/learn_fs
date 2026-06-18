# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/group.h

This header declares ext4 group descriptor checksum and bitmap initialization helpers.

Content:
- Prototypes for `ext4_group_desc_csum`, `ext4_group_desc_csum_verify`, `ext4_read_block_bitmap`, `ext4_init_block_bitmap`, `ext4_init_inode_bitmap`, and `mark_bitmap_end`.
- Macro `ext4_free_blocks_after_init` aliases to `ext4_init_block_bitmap`.

Role:
- Supports ext4 group descriptor validation and lazy bitmap initialization code paths.
- Complements the group descriptor definitions in `ext3_fs.h`.
