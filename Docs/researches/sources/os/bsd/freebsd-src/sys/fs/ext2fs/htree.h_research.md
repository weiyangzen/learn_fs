# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/htree.h

## Purpose
Declares ext3/ext4 HTree indexed-directory constants and on-disk/in-memory helper structures.

## Main Elements
- Defines hash version constants: legacy, half-MD4, TEA, and unsigned variants.
- Defines `EXT2_HTREE_EOF`.
- Provides fake directory-entry layout used at HTree roots and nodes.
- Defines HTree count, entry, tail checksum, root info, root block, and node structures.
- Defines lookup state structures for up to two HTree levels.
- Defines `ext2fs_htree_sort_entry` for sorting directory entries by hash during splits/index creation.

## Dependencies And Integration
Used by ext2 htree lookup/add/create and checksum code. `ext2_lookup.c` calls HTree lookup first for indexed directories and falls back to linear scan on unsupported or failed paths.

## Risk Notes
The structures mirror disk format and must remain packed-compatible with ext filesystem expectations. Hash version/sign selection depends on superblock fields from `ext2fs.h`.
