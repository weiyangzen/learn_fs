# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/freefs.c

## Role

Releases an `ext2_filsys` handle and associated library-owned resources.

## Main Flow

- `ext2fs_free()` closes image and primary I/O channels, frees names, superblocks, group descriptors, bitmaps, badblocks, directory block list, inode cache, MMP buffers, and shared-block SHA hashmap.
- Clears filesystem magic and calls `ext2fs_zero_blocks2(NULL, 0, 0, NULL, NULL)` to reset zero-block state.
- Provides helpers to free badblocks/u32 lists and directory block lists.

## Dependencies

Uses I/O channel close, bitmap free, inode-cache free, badblocks free, and hashmap free.

## Risks / Notes

- Silently returns for null or invalid filesystem magic.
- `ext2fs_u32_list_free()` assumes non-null input and only checks magic.
