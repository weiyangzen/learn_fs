# File Research: sources/os/linux/linux/fs/minix/minix.h

## Purpose
Defines Minix filesystem private VFS structures, version constants, function declarations, helpers, and bitmap bit-operation compatibility logic.

## Main Responsibilities
- Declare the in-memory Minix inode and superblock private data.
- Expose Minix inode/block allocation, raw inode access, directory, file, and tree helper APIs.
- Provide `minix_sb()` and `minix_i()` container helpers.
- Provide bitmap operation macros for native-endian, big-endian 16-bit indexed, and little-endian Minix bitmap formats.
- Define the `minix_error_inode()` logging macro.

## Key Structures
- `struct minix_inode_info`
  - Holds V1 `__u16 i1_data[16]` or V2/V3 `__u32 i2_data[16]`.
  - Tracks metadata buffer heads in `i_metadata_bhs`.
  - Embeds the VFS `struct inode`.
- `struct minix_sb_info`
  - Stores inode/zone counts, bitmap block counts, first data zone, log zone size, directory entry size, maximum name length, bitmap buffer arrays, superblock buffer, raw superblock pointer, mount state, and Minix version.

## Key Constants
- `MINIX_V1`, `MINIX_V2`, `MINIX_V3`.
- `INODE_VERSION(inode)` resolves the mounted Minix version from the superblock.
- `minix_blocks_needed(bits, blocksize)` computes bitmap block requirements.

## Declared API Groups
- Inode lifecycle and raw inode access:
  - `minix_iget()`, `minix_new_inode()`, `minix_free_inode()`.
  - `minix_V1_raw_inode()`, `minix_V2_raw_inode()`.
- Block bitmap allocation:
  - `minix_new_block()`, `minix_free_block()`, count helpers.
- File/block mapping:
  - `V1_minix_get_block()`, `V2_minix_get_block()`, truncate and block-count helpers.
- Directory operations:
  - `minix_find_entry()`, `minix_add_link()`, `minix_delete_entry()`, `minix_make_empty()`, `minix_empty_dir()`, `minix_set_link()`, `minix_dotdot()`, `minix_inode_by_name()`.
- VFS operation tables:
  - file, directory, and inode operation tables.

## Bitmap Endianness Behavior
The header supports three bitmap encodings:
- Native-endian bit operations for native Minix bitmap configurations.
- Big-endian 16-bit indexed bitmaps with custom `minix_find_first_zero_bit()` and bit-number swizzling.
- Default little-endian bit operations using Linux little-endian bit helpers.

A compile-time error rejects simultaneously enabling native-endian and big-endian 16-bit indexed modes.

## Important Behaviors and Edge Cases
- `minix_find_first_zero_bit()` has a custom implementation for big-endian 16-bit indexed bitmaps.
- `minix_test_bit()` differs between endian modes.
- The `minix_error_inode()` macro records function and line number automatically.

## Research Notes
This header is the coordination point for all Minix source files. It is especially important for understanding how old on-disk bitmap formats are abstracted behind uniform allocation helpers.
