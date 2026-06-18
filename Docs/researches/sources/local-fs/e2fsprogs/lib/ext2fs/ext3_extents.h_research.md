# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext3_extents.h

## Purpose
Defines ext3/ext4 extent-tree on-disk structures and helper macros.

## Key Structures
- `struct ext3_extent_tail`: checksum tail for extent blocks.
- `struct ext3_extent`: leaf extent mapping logical block range to physical block start.
- `struct ext3_extent_idx`: interior index entry pointing to a lower-level extent block.
- `struct ext3_extent_header`: common header for inode-root and external extent blocks.
- `struct ext3_ext_path`: kernel-style traversal path structure.

## Constants and Macros
- `EXT3_EXT_MAGIC`: extent header magic.
- `EXT_INIT_MAX_LEN`: max initialized extent length.
- `EXT_UNINIT_MAX_LEN`: max uninitialized extent length.
- `EXT_MAX_EXTENT_LBLK`, `EXT_MAX_EXTENT_PBLK`.
- Entry navigation macros:
  - `EXT_FIRST_EXTENT`
  - `EXT_FIRST_INDEX`
  - `EXT_HAS_FREE_INDEX`
  - `EXT_LAST_EXTENT`
  - `EXT_LAST_INDEX`
  - `EXT_MAX_EXTENT`
  - `EXT_MAX_INDEX`

## Integration
Used directly by `extent.c` and exposed through `ext2fs.h`. These structures are serialized to disk, including the root extent header stored inside `inode->i_block`.

## Risks and Notes
- `ee_len` encodes initialized vs uninitialized state via the high bit convention.
- Extent tree layout depends on 12-byte extent/index entries and available block tail space.
