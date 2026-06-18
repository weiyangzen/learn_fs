# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/badblocks.c

## Purpose
Implements sorted 32-bit list primitives used for bad block lists and similar u32 tracking lists.

## Main Elements
- `make_u32_list()`: allocates and initializes list storage.
- Creation/copy wrappers: `ext2fs_u32_list_create()`, `ext2fs_badblocks_list_create()`, `ext2fs_u32_copy()`, `ext2fs_badblocks_copy()`.
- `ext2fs_u32_list_add()` / badblocks wrapper: inserts unique values in sorted order, growing by 100 entries when full.
- `ext2fs_u32_list_find()` and test wrappers: binary search for values.
- `ext2fs_u32_list_del()` and badblocks delete wrapper: remove a value and compact the list.
- Iterator API: begin, next, end for u32 and badblocks aliases.
- Equality/count helpers: compare list contents and return count.

## Dependencies And Integration
Defines the core in-memory list used by bad block import, bad block inode creation, and compatibility wrappers. Uses libext2fs memory helpers and magic checks.

## Risk Notes
The list stores `__u32`/`blk_t` style values, so it represents legacy 32-bit block lists. Copy creation copies `bb->size` entries, not just `num`, assuming full allocation is initialized.
