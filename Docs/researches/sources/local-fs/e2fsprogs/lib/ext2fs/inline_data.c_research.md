# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/inline_data.c

## Role

Implements ext4 inline data support for files and directories, where initial payload lives in inode `i_block` plus optional `system.data` xattr.

## Main Flow

- Private EA helpers read/write/remove `system.data`.
- `ext2fs_inline_data_init()` creates empty inline-data EA.
- `ext2fs_inline_data_size()` reports inline capacity/size from inode plus EA.
- `ext2fs_inline_data_dir_iterate()` exposes inline directory entries to the normal directory-iteration callback machinery, including synthetic `.` and `..` entries.
- `ext2fs_inline_data_expand()` converts inline file/directory data to normal block-backed storage.
- `ext2fs_inline_data_get()` and `ext2fs_inline_data_set()` copy inline bytes between inode/xattr storage and caller buffers.

## Important Details

- Directory expansion builds a full directory block, adds metadata checksum tail when needed, allocates a block, writes it, updates inode flags/size/block map, and updates block allocation stats.
- File expansion clears inline state, writes inode, opens the file through `fileio.c`, and writes buffered contents normally.
- Expansion deliberately writes inode, removes EA, then rereads inode to avoid stale EA-block state causing block aliasing.
- Big-endian directory data paths swap directory entries in and out.

## Dependencies

Uses xattr APIs, inode read/write, directory iteration processing, block allocator, bmap, inode block accounting, file I/O, dir block write, and metadata checksum helpers.

## Risks / Notes

- Conversion is multi-step and not transactional; failures after block allocation or inode mutation can leave partial state.
- `ext2fs_inline_data_set()` requires existing inline data state for size accounting and returns `EXT2_ET_INLINE_DATA_NO_SPACE` when xattr/inode inline capacity is insufficient.
