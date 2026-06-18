# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/fileio.c

## Role

Implements a buffered file abstraction over ext2/ext4 inodes: open, read, write, seek, flush, close, get size, and set size.

## Main Flow

- `ext2fs_file_open2()` allocates `struct ext2_file`, loads or copies the inode, and allocates a three-block buffer area. `BMAP_BUFFER` points at extra space used by block mapping.
- `ext2fs_file_flush()` writes dirty buffered data, allocating a physical block if needed and converting uninitialized extents before writing.
- `sync_buffer_position()` and `load_buffer()` keep the one-block cache aligned with `file->pos`.
- `ext2fs_file_read()` reads regular block-mapped data, with a separate `ext2fs_file_read_inline_data()` path for `EXT4_INLINE_DATA_FL`.
- `ext2fs_file_write()` writes regular data, expanding inline data when necessary and allocating blocks via `ext2fs_bmap2`.
- `ext2fs_file_set_size2()` updates inode size, zeros tail bytes past EOF, writes the inode, and punches truncated blocks.

## Important Details

- The file object stores its own inode copy. If opened with a caller-supplied inode, inline-data expansion comments note that external inode state cannot be updated directly.
- For shared duplicate block mode (`EXT2_FLAG_SHARE_DUP`), writes hash full block contents with SHA-512 and consult `fs->block_sha_map` before allocating a new block.
- Reads from holes or uninitialized extents return zeroed buffers.
- Writes require `EXT2_FILE_WRITE`; creation/write on read-only filesystems is rejected at open time.

## Dependencies

Uses `ext2fs_bmap2`, `io_channel_read_blk64`, `io_channel_write_blk64`, inline data helpers from `inline_data.c`, punching/truncation, inode read/write, SHA-512, and hashmap support.

## Risks / Notes

- The single-block buffer means random small writes cause frequent flush/load cycles.
- Deduplication stores key pointers rather than copied key bytes; in current use the key points inside the stored `block_entry`, which is safe only as long as that ownership pattern is preserved.
- On close, flush errors are returned after memory is freed; callers cannot retry through the same file object.
