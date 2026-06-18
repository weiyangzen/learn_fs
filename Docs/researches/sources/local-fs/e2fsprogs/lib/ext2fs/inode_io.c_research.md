# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/inode_io.c

## Role

Implements an `io_manager` that treats a filesystem inode as an I/O channel.

## Main Flow

- `ext2fs_inode_io_intern2()` creates an interned name and private data object for a target inode, optionally carrying a caller-provided inode copy.
- `inode_open()` consumes the interned object, creates an `io_channel`, opens the inode via `ext2fs_file_open2()`, and attaches private data.
- Read/write block operations seek in the ext2 file abstraction and read/write byte counts based on channel block size.
- `inode_write_byte()` writes arbitrary bytes at an offset.
- `inode_flush()` delegates to `ext2fs_file_flush()`.
- `inode_close()` closes the file, releases private data, name, and channel.

## Dependencies

Uses `fileio.c` APIs and the generic I/O manager struct contract.

## Risks / Notes

- Interned names are stored in a global linked list; this is not thread-safe.
- `inode_open()` removes the interned entry even if later allocation/open steps fail, so failed opens cannot be retried with the same name.
- The channel default block size is 1024 until set by caller.
