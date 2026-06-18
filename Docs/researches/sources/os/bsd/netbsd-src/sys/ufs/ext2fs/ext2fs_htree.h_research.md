# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_htree.h

This header defines ext3 HTree directory-index constants and structures.

Key definitions:
- Hash version constants: legacy, half-MD4, TEA, and unsigned variants.
- `EXT2_HTREE_EOF`
- `struct ext2fs_fake_direct`: fake directory entry header used in HTree nodes.
- `struct ext2fs_htree_count`: count/limit overlay for the first entry slot.
- `struct ext2fs_htree_entry`: hash-to-block index entry.
- `struct ext2fs_htree_root_info`: root metadata including hash version, info length, and index levels.
- `struct ext2fs_htree_root`: directory block 0 format containing fake `.`/`..`, root info, and entries.
- `struct ext2fs_htree_node`: non-root index node format.
- `struct ext2fs_htree_lookup_level` and `struct ext2fs_htree_lookup_info`: traversal state for up to two levels.
- `struct ext2fs_htree_sort_entry`: temporary descriptor used when splitting directory blocks.

Dependencies:
- Uses fixed-width integer types and `struct buf`.

Design notes:
- The fixed `h_levels[2]` traversal state matches the implementation’s maximum supported HTree depth.
