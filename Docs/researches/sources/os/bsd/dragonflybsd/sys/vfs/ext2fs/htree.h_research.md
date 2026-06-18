# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/htree.h

Defines data structures and constants for ext3/ext4 HTree indexed directories. It contains only declarations and layout definitions, not algorithmic code.

Hash version constants cover legacy, half-MD4, TEA, and unsigned variants. `EXT2_HTREE_EOF` defines the terminal logical offset marker used by directory iteration.

`struct ext2fs_fake_direct` models a directory-entry-like header used inside HTree blocks. `struct ext2fs_htree_count` and `struct ext2fs_htree_entry` define count/limit metadata and hash-to-block entries. `struct ext2fs_htree_tail` stores the metadata checksum at the end of HTree blocks.

`struct ext2fs_htree_root_info`, `struct ext2fs_htree_root`, and `struct ext2fs_htree_node` define root and interior/index block layouts. The root embeds fake `.` and `..` entries followed by hash metadata and flexible entries.

Lookup helpers are represented by `struct ext2fs_htree_lookup_level` and `struct ext2fs_htree_lookup_info`, supporting up to two levels. `struct ext2fs_htree_sort_entry` supports sorting directory entries by hash/offset/size.

Important dependencies: used by ext2 directory lookup/update/checksum code outside this file. `ext2_vnops.c` references htree-aware checksum update behavior during rename.

Notable risks or research hooks: structures use zero-length arrays for flexible entries, which is traditional kernel C but relevant for bounds auditing in directory parsing.
