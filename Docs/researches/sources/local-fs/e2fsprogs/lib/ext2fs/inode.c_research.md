# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/inode.c

## Role

Central inode read/write, scan, cache, and validation implementation.

## Main Flow

- Inode cache helpers create, flush, and free a small direct-mapped-ish cache of recently read inodes and one block buffer.
- `ext2fs_open_inode_scan()` prepares buffered inode-table scanning, loads badblock state if needed, handles lazy inode-table metadata, and allocates scan buffers.
- `ext2fs_get_next_inode_full()` iterates inodes, crossing groups and blocks, handling missing tables, bad inode-table blocks, checksum verification, endian conversion, and garbage detection.
- `ext2fs_read_inode2()` reads one inode from normal filesystem or image-file layout, uses cache, verifies checksum, and supports override callbacks.
- `ext2fs_write_inode2()` prepares a full-size shadow inode, updates cache, sets checksum, reads/modifies/writes inode-table blocks, and marks filesystem changed.
- `ext2fs_write_new_inode()` initializes timestamps and large-inode extra fields before writing.
- `ext2fs_get_blocks()` and `ext2fs_check_directory()` provide simple inode block and directory validation helpers.

## Important Details

- Scan sanity checks can mark entire inode-table blocks as checksum-clean or garbage based on per-inode checksum and block-map/extent sanity.
- Group descriptor checksum support enables lazy scan skipping for `EXT2_BG_INODE_UNINIT`.
- Reads support `READ_INODE_NOCSUM`; writes support `WRITE_INODE_NOCSUM`.
- Image-file mode reads inode data from image header offsets and `fs->image_io`.

## Dependencies

Uses group descriptor helpers, inode checksum helpers, I/O channels, badblocks list, image header layout, endian swap helpers, and ext2fs callbacks.

## Risks / Notes

- `ext2fs_free_inode_cache()` decrements refcount before freeing; callers must only pass valid cache pointers.
- Single-inode writes read the containing block first, so write errors can originate from read-modify-write setup.
- Garbage detection is heuristic and can return `EXT2_ET_INODE_IS_GARBAGE` instead of a raw checksum error.
