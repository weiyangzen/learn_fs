# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_extents.h

This header defines ext4 extent on-disk structures, constants, cache state, path state, helper macros, and exported extent APIs.

Key responsibilities:
- Define extent magic, maximum logical range constants, and maximum depth.
- Define cache result constants.
- Declare extent tail, extent, extent index, extent header, extent cache, and extent path structures.
- Provide macros for locating first/last/max extent/index entries and checksum tail offsets.
- Declare extent tree operations used by allocation, mapping, truncation, and debug code.

Important definitions:
- `EXT4_EXT_MAGIC`, `EXT4_MAX_BLOCKS`, `EXT_INIT_MAX_LEN`, `EXT4_MAX_LEN`, `EXT4_EXT_DEPTH_MAX`.
- `EXT4_EXT_CACHE_NO`, `EXT4_EXT_CACHE_GAP`, `EXT4_EXT_CACHE_IN`.
- `struct ext4_extent_tail`, `struct ext4_extent`, `struct ext4_extent_index`, `struct ext4_extent_header`.
- `struct ext4_extent_cache`, `struct ext4_extent_path`.
- `EXT_FIRST_EXTENT`, `EXT_FIRST_INDEX`, `EXT_LAST_EXTENT`, `EXT_LAST_INDEX`, `EXT4_EXTENT_TAIL_OFFSET`, `EXT_HAS_FREE_INDEX`.

Important interactions:
- Included by extent implementation, bmap/balloc/truncate paths, checksum code, and inode conversion/debug paths.
