# File Research: sources/os/linux/linux/fs/f2fs/verity.c

Implements F2FS-specific `fsverity_operations`.

Key behavior:
- Stores fs-verity metadata past EOF, starting at the first 64 KiB boundary after `i_size`.
- Uses pagecache-level read/write helpers because verity metadata must be read and written beyond `i_size`, and enabling verity may use a read-only file descriptor.
- `pagecache_write()` bounds metadata writes against `max_file_blocks(inode)` and writes through the address-space `write_begin`/`write_end` path.
- Uses a compact F2FS verity xattr containing:
  - format version
  - descriptor size
  - descriptor position in file data
- Stores only the descriptor location in the xattr because verity metadata must be encrypted when the file is encrypted, while F2FS xattrs are not encrypted.
- `f2fs_begin_enable_verity()` rejects concurrent verity enable, rejects atomic files, initializes quota, converts inline data out of the inode, and sets `FI_VERITY_IN_PROGRESS`.
- `f2fs_end_enable_verity()` writes the descriptor after the Merkle tree, flushes all file/verity pages, sets the verity xattr, sets the inode verity flag, persists inode flags, and clears in-progress state.
- On enable failure, truncates cached and on-disk verity metadata beyond `i_size`, takes the inode GC write semaphore to prevent GC from re-instantiating pages, and marks the filesystem for fsck if truncation fails.
- `f2fs_get_verity_descriptor()` reads and validates the descriptor-location xattr, checks bounds and overflow, reports corrupted verity xattrs through `f2fs_handle_error()`, and reads the descriptor from pagecache.
- Merkle tree page read, readahead, and write operations translate fs-verity-relative offsets by the F2FS metadata start position.
- Exports `f2fs_verityops` with begin/end enable, descriptor lookup, Merkle page read, readahead, and Merkle block write callbacks.

Important interactions:
- `super.c` installs `f2fs_verityops` into `sb->s_vop` when `CONFIG_FS_VERITY` is enabled.
- Depends on F2FS xattr APIs for the verity descriptor-location xattr.
- Depends on F2FS quota, inline-data conversion, truncate, inode dirtying, GC locking, and corruption/error reporting.
