# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/dir_iterate.c

Implements directory entry iteration and directory record length encoding helpers. The main API is `ext2fs_dir_iterate2`; `ext2fs_dir_iterate` is a legacy callback wrapper.

Record length helpers:
- `ext2fs_get_rec_len` decodes `dirent->rec_len`, including ext4 encodings for block sizes >= 64 KiB.
- `ext2fs_set_rec_len` validates and encodes record lengths, rejecting misaligned or oversized values.

Iteration behavior:
- `ext2fs_dir_iterate2` validates the inode as a directory, prepares a `dir_context`, and runs `ext2fs_block_iterate3` in read-only mode with `ext2fs_process_dir_block`.
- Inline-data directories are handled by `ext2fs_inline_data_dir_iterate` when block iteration reports inline data.
- `ext2fs_process_dir_block` reads a directory block, verifies record structure, invokes the callback, tracks changed entries, and writes back changed blocks.
- It can include empty, removed, checksum, or inline-data entries based on flags.
- Deleted-entry detection uses `ext2fs_validate_entry` to inspect slack space for plausible removed entries.

Error handling:
- Corrupt record lengths, bad name lengths, or out-of-block records set `EXT2_ET_DIR_CORRUPTED`.
- Changed inline data returns `BLOCK_INLINE_DATA_CHANGED` to notify the inline-data caller.
- Callback `DIRENT_ABORT` stops processing.

Dependencies: block iterator, directory block read/write, metadata checksum support, inline data support.

Implementation notes:
- Checksum tail entries are normally skipped unless `DIRENT_FLAG_INCLUDE_CSUM` is set.
- The iterator distinguishes dot, dotdot, and other entries using entry ordinal state.
