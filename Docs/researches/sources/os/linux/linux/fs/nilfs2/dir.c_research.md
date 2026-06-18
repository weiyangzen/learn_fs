# File Research: sources/os/linux/linux/fs/nilfs2/dir.c

This file implements NILFS2 directory entry operations, derived from ext2-style page-cache directory handling and adapted for NILFS2’s block/chunk and transaction model.

Directory format:
- Directory records use `struct nilfs_dir_entry`, little-endian inode and record length fields, and ext-style variable-length entries.
- `nilfs_rec_len_from_disk()` and `nilfs_rec_len_to_disk()` handle the 64KiB page-size special record length encoding.
- Directory chunks are filesystem block-sized.

Validation:
- `nilfs_check_folio()` verifies a directory folio:
  - directory size aligns to chunk size
  - record length is minimal and 4-byte aligned
  - record length is large enough for name length
  - entries do not span block-sized chunks
  - private NILFS inode numbers do not appear in user directories
- Bad entries log detailed metadata errors and fail the folio read with `-EIO`.

Lookup/read:
- `nilfs_get_folio()` reads and maps a directory folio, validating it once via the checked flag.
- `nilfs_readdir()` emits entries through `dir_emit()`, advancing `ctx->pos` by record length.
- `nilfs_find_entry()` searches from cached `i_dir_start_lookup`, wraps around, and returns a mapped folio plus entry.
- `nilfs_inode_by_name()` returns the inode number for a named directory entry.
- `nilfs_dotdot()` validates and returns the `..` entry in the first directory block.

Mutation:
- `nilfs_add_link()` finds free space or expands at `i_size`, splits existing entries when needed, writes name/inode/type, commits the modified chunk, updates directory times, and marks the inode dirty.
- `nilfs_set_link()` replaces a directory entry target under folio lock and commits the containing record range.
- `nilfs_delete_entry()` removes an entry by merging its record length into the previous entry when possible.
- `nilfs_make_empty()` creates the initial `.` and `..` records for a new directory.
- `nilfs_empty_dir()` verifies only `.` and `..` entries are present for rmdir.

Write integration:
- Chunk modification uses `nilfs_prepare_chunk()` with `__block_write_begin()` and `nilfs_get_block()`.
- `nilfs_commit_chunk()` updates `i_size`, sets sync transaction flag for dirsync directories, counts newly dirtied buffers, marks the file dirty, and unlocks the folio.

Exported operations:
- `nilfs_dir_operations` provides llseek, read dir, shared iteration, ioctl/compat ioctl, fsync, and lease handling.
