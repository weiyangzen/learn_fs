# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ind_block.c

## Role

Reads and writes legacy indirect block pointer blocks.

## Main Flow

- `ext2fs_read_ind_block()` reads a block through the filesystem I/O channel, or returns zeros when operating on image-file mode with separate image I/O.
- On big-endian hosts, read swaps each 32-bit block pointer to CPU order.
- `ext2fs_write_ind_block()` skips writes in image-file mode and swaps pointers before writing on big-endian hosts.

## Dependencies

Uses `io_channel_read_blk` / `io_channel_write_blk` and ext2fs byte-swap helpers.

## Risks / Notes

- Big-endian write swaps the caller’s buffer in place before writing and does not swap it back, so callers must account for destructive conversion.
