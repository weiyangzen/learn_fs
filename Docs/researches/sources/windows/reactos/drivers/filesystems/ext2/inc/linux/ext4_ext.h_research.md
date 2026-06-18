# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext4_ext.h

This header defines ext4 extent on-disk structures and helper functions.

Key structures:
- `ext4_extent_tail`: extent block checksum tail.
- `EXT4_EXTENT`: leaf extent with logical start, length/unwritten bit, and 48-bit physical start.
- `EXT4_EXTENT_IDX`: internal index entry with logical start and 48-bit leaf pointer.
- `EXT4_EXTENT_HEADER`: extent tree header with magic, entries, max entries, depth, and generation.
- `struct ext4_ext_path`: traversal state for extent lookup, split, insert, and truncate operations.

Key macros/helpers:
- `EXT4_EXT_MAGIC`, `get_ext4_header`, extent tail offset/finder.
- Entry navigation macros for first/last/max extent or index.
- `ext_inode_hdr`, `ext_block_hdr`, and `ext_depth`.
- Initialized/unwritten length helpers using `EXT_INIT_MAX_LEN`.
- Physical block load/store helpers for extents and indexes.
- `INODE_HAS_EXTENT`, `ext_to_block`, `idx_to_block`.
- `ext4_ext_dirty` wrapper macro.

Declared APIs:
- `ext4_ext_get_blocks`
- `ext4_ext_tree_init`
- `ext4_ext_truncate`

Role:
- Enables ext4 extent-tree mapping and truncation paths within the Ext2Fsd driver.
- Uses packed on-disk structs and local endian assumptions through the included ext4/ext3 compatibility layer.
