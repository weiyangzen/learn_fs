# File Research: sources/os/linux/linux/fs/ext4/ext4_extents.h

## Purpose

`ext4_extents.h` defines ext4’s extent tree on-disk structures and small helper routines for extent traversal, extent length state, physical block packing, and KUnit-test-visible extent hooks.

## Main Definitions

- `struct ext4_extent_tail`
  - Stores the checksum at the end of non-inode extent blocks.
  - Checksum covers filesystem UUID, inode number, and extent block data.

- `struct ext4_extent`
  - Leaf extent record.
  - Fields:
    - `ee_block`: first logical block covered.
    - `ee_len`: extent length and unwritten-state encoding.
    - `ee_start_hi` / `ee_start_lo`: split physical block address.

- `struct ext4_extent_idx`
  - Internal extent-tree index record.
  - Fields:
    - `ei_block`: logical block range covered by child.
    - `ei_leaf_lo` / `ei_leaf_hi`: child extent/index block physical address.
    - `ei_unused`: padding.

- `struct ext4_extent_header`
  - Present at each extent tree node, including the inode-root node.
  - Tracks magic, current entries, maximum entries, tree depth, and generation.

- `struct ext4_ext_path`
  - Runtime path used while traversing or modifying the extent tree.
  - Holds physical block, depth, max depth, current extent/index/header, and buffer head.

- `struct partial_cluster`
  - Used during extent removal for bigalloc cluster boundary handling.
  - Tracks physical cluster, logical block, and whether the partial cluster is initial, freeable, or not freeable.

## Constants and Encoding

- `EXT4_EXT_MAGIC` is the extent header magic.
- `EXT4_MAX_EXTENT_DEPTH` caps extent tree depth at 5.
- `EXT_INIT_MAX_LEN` is 32768 blocks.
- `EXT_UNWRITTEN_MAX_LEN` is 32767 blocks.
- `ee_len` uses its high bit to encode unwritten extents:
  - values up to `0x8000` are initialized extents.
  - values above `0x8000` are unwritten extents with actual length adjusted by subtracting `EXT_INIT_MAX_LEN`.
  - `0x8000` is a special initialized 32768-block extent.

## Helper Macros and Functions

- Tree navigation:
  - `EXT_FIRST_EXTENT`
  - `EXT_FIRST_INDEX`
  - `EXT_LAST_EXTENT`
  - `EXT_LAST_INDEX`
  - `EXT_MAX_EXTENT`
  - `EXT_MAX_INDEX`
  - `EXT_HAS_FREE_INDEX`
- Header access:
  - `ext_inode_hdr()` returns the inode-root extent header from `EXT4_I(inode)->i_data`.
  - `ext_block_hdr()` returns the extent header from a buffer head.
  - `ext_depth()` returns the inode-root tree depth.
- Tail access:
  - `EXT4_EXTENT_TAIL_OFFSET()`
  - `find_ext4_extent_tail()`
- Extent state:
  - `ext4_ext_mark_unwritten()`
  - `ext4_ext_is_unwritten()`
  - `ext4_ext_get_actual_len()`
  - `ext4_ext_mark_initialized()`
- Physical block packing:
  - `ext4_ext_pblock()` combines `ee_start_lo` and `ee_start_hi`.
  - `ext4_idx_pblock()` combines `ei_leaf_lo` and `ei_leaf_hi`.
  - `ext4_ext_store_pblock()` splits a physical block into extent fields.
  - `ext4_idx_store_pblock()` splits a physical block into index fields.

## Declared APIs

- `__ext4_ext_dirty()` marks extent metadata dirty under a journal handle.
- `ext4_ext_zeroout()` zeroes blocks covered by an extent.
- Under `CONFIG_EXT4_KUNIT_TESTS`, exposes:
  - `ext4_ext_space_root_idx_test()`
  - `ext4_split_convert_extents_test()`

## Dependencies

- Includes `ext4.h`, so it depends on ext4 inode types, block types, buffer heads, endian helpers, and JBD2 handle declarations.

## Research Notes

This header is small but encodes the core extent ABI. The most important invariant is the overloaded `ee_len` high bit: callers must use the helper functions rather than raw length arithmetic when unwritten extents are possible.
