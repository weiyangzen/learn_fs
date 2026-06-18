# File Research: sources/os/linux/linux-stable/fs/ext4/ext4_extents.h

## Summary
Defines ext4's extent tree on-disk structures, in-memory traversal path, extent length/state helpers, physical block packing helpers, and KUnit-visible extent testing hooks.

## Main Responsibilities
- Describes the extent block tail checksum record.
- Defines leaf extents, internal extent indexes, and extent block headers.
- Defines `struct ext4_ext_path`, the traversal state used by lookup, insertion, split, truncate, and conversion paths.
- Defines `struct partial_cluster` for bigalloc-aware extent removal decisions.
- Provides macros for locating first, last, and maximum extents or indexes inside a header.
- Provides inline helpers for root/in-block headers, tree depth, unwritten/initialized state, logical length, and physical block encoding.

## Important Details
Extent blocks use a 12-byte header followed by either extents or indexes. Non-inode extent blocks can store `struct ext4_extent_tail` at the end of the block for metadata checksums without rebalancing the tree.

`ee_len` encodes both length and unwritten state. Initialized extents can reach `EXT_INIT_MAX_LEN` blocks. Unwritten extents use the high bit and can reach `EXT_UNWRITTEN_MAX_LEN`; the exact value `0x8000` is treated as initialized length 32768 rather than unwritten length zero.

Physical blocks are split into low 32-bit and high 16-bit fields in both extents and indexes. `ext4_ext_pblock()`, `ext4_idx_pblock()`, `ext4_ext_store_pblock()`, and `ext4_idx_store_pblock()` are the canonical conversions.

## Key APIs
- `__ext4_ext_dirty()`.
- `ext4_ext_zeroout()`.
- KUnit-only `ext4_ext_space_root_idx_test()` and `ext4_split_convert_extents_test()` when `CONFIG_EXT4_KUNIT_TESTS` is enabled.

## Dependencies
Includes `ext4.h` and uses ext4 inode state, buffer heads, JBD2 handles, and logical/physical block typedefs. The main implementation lives in `extents.c`.

## Risks
Extent tree correctness depends on careful endian conversion and exact interpretation of `ee_len`. `struct ext4_ext_path` contains raw pointers into inode or buffer-head extent blocks; callers must preserve buffer lifetime and update dirty state through the journaling path.
