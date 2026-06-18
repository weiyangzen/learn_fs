# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/link.c

Implements directory entry creation via `ext2fs_link()` plus htree-indexed directory support. It handles both linear directories and indexed ext4 htree directories.

The linear path uses `link_proc()` over directory iteration, absorbing adjacent empty entries, splitting oversized entries, writing inode/name/type fields, and honoring metadata checksum tail space. It can append only to the last block when `EXT2FS_LINK_APPEND` is set.

The indexed path performs htree lookup, directory hash calculation with casefold support, leaf insertion, leaf splitting, internal node splitting, tree-depth growth, and conversion of a one-block directory into an indexed directory when the filesystem supports dir_index.

Important symbols: `dx_lookup`, `dx_split_leaf`, `dx_grow_tree`, `try_make_indexed_dir`, `ext2fs_dir_is_dx`, `ext2fs_inc_nlink`, `ext2fs_dec_nlink`, `ext2fs_dir_link_max`, and `ext2fs_dir_link_empty`.

Key invariants: directory block checksum tails reduce usable entry space; htree hash version must be supported; uninitialized mapped blocks are treated as corruption; directory nlink overflow can be represented as `i_links_count == 1` for indexed directories when the feature permits it.
