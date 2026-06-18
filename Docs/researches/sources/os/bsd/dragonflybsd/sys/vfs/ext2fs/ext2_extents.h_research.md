# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_extents.h

This header defines ext4 extent on-disk structures, extent tree constants, cache state constants, path descriptors, and prototypes used by the DragonFlyBSD ext2 extent stubs/checksum code.

Key responsibilities:
- Define extent magic, maximum block/length/depth constants, and cache result states.
- Declare on-disk extent, index, header, and checksum tail structures.
- Provide macros for locating first/last/max extent or index entries and extent checksum tail position.
- Declare extent tree API prototypes used by allocation, bmap, truncate, and debug code.

Important definitions:
- `EXT4_EXT_MAGIC`, `EXT4_MAX_BLOCKS`, `EXT4_MAX_LEN`, `EXT4_EXT_DEPTH_MAX`.
- `EXT4_EXT_CACHE_NO`, `EXT4_EXT_CACHE_GAP`, `EXT4_EXT_CACHE_IN`.
- `struct ext4_extent_tail`, `struct ext4_extent`, `struct ext4_extent_index`, `struct ext4_extent_header`.
- `struct ext4_extent_cache` and `struct ext4_extent_path`.
- `EXT_FIRST_EXTENT`, `EXT_FIRST_INDEX`, `EXT_LAST_EXTENT`, `EXT_LAST_INDEX`, `EXT4_EXTENT_TAIL_OFFSET`, `EXT_HAS_FREE_INDEX`, `EXT_MAX_EXTENT`, `EXT_MAX_INDEX`.

Important interactions:
- Included by `ext2_extents.c`, `ext2_csum.c`, `ext2_subr.c`, and inode conversion/debug paths.

Notable behavior:
- The data structures are complete enough for checksum and flag representation, but `ext2_extents.c` does not implement real extent operations in this tree.
