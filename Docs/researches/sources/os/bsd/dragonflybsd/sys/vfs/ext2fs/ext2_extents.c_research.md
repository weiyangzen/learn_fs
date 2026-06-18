# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_extents.c

This file is a mostly stubbed ext4 extent implementation. It declares the expected extent helpers and trace provider, but the functional extent operations either return neutral values, `NULL`, cache miss, or `EINVAL`.

Key responsibilities:
- Provide symbols expected by the rest of the ext2fs code when ext4 extent feature bits are present.
- Define optional debug print hooks under `EXT2FS_PRINT_EXTENTS`.
- Stub tree initialization, lookup, cache, allocation, and truncate operations.

Important functions:
- `ext4_ext_tree_init`: No-op placeholder called for new regular files/directories when extents are supported.
- `ext4_ext_in_cache`: Always reports `EXT4_EXT_CACHE_NO`.
- `ext4_ext_find_extent`: Returns `EINVAL`.
- `ext4_ext_get_blocks`: Returns `EINVAL`.
- `ext4_ext_remove_space`: Returns `EINVAL`.
- Inline helpers such as `ext4_ext_inode_header`, `ext4_ext_block_header`, `ext4_ext_index_pblock`, and `ext4_ext_extent_pblock`: Return `NULL` or zero.

Important interactions:
- Called from `ext2_valloc`, `ext2_balloc`, `ext2_bmap`, and `ext2_truncate` when `IN_E4EXTENTS` is set.
- The checksum file supports extent block checksums even though this implementation does not manipulate extent trees.

Notable behavior and risks:
- Extent-backed files cannot be allocated, mapped, or truncated successfully through these stubs.
- The presence of `IN_E4EXTENTS` changes dispatch behavior elsewhere, so this file defines a clear unsupported path rather than falling back to indirect blocks.
