# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/bb_compat.c

## Purpose
Provides legacy `badblocks_*` API names as thin wrappers around the `ext2fs_badblocks_*` API.

## Main Elements
- `badblocks_list_create()`, `badblocks_list_free()`, `badblocks_list_add()`, `badblocks_list_test()`.
- Iterator wrappers: `badblocks_list_iterate_begin()`, `badblocks_list_iterate()`, `badblocks_list_iterate_end()`.

## Dependencies And Integration
Includes `ext2fsP.h` and forwards directly to the modern libext2fs badblocks functions. This preserves older caller/source compatibility.

## Risk Notes
No independent logic; behavior and limitations are inherited from `badblocks.c` and list-free implementation elsewhere.
