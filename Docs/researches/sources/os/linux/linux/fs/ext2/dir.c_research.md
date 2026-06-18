# File Research: sources/os/linux/linux/fs/ext2/dir.c

Read status: complete, 739 lines.

This file implements ext2 directory record handling using the page cache/folios. It owns directory entry validation, iteration, lookup-by-name, insertion, deletion, empty-directory checks, and directory file operations.

Key responsibilities:
- Converts directory record lengths between disk and memory, including 64 KiB block-size handling.
- Validates directory folios with `ext2_check_folio()`.
- Reads and maps directory folios through `ext2_get_folio()`.
- Iterates directories with `ext2_readdir()`.
- Finds named entries via `ext2_find_entry()` and finds `..` via `ext2_dotdot()`.
- Adds directory entries with `ext2_add_link()`.
- Updates existing entries with `ext2_set_link()`.
- Deletes entries with `ext2_delete_entry()`.
- Creates `.` and `..` entries with `ext2_make_empty()`.
- Checks rmdir emptiness with `ext2_empty_dir()`.
- Exposes `ext2_dir_operations`.

Directory format behavior:
- Directories are block-sized chunks containing variable-length `ext2_dir_entry_2` records.
- Entries must be 4-byte aligned, fit within a chunk, have sufficient `rec_len` for `name_len`, and reference valid inode numbers.
- Deletion merges the removed record into the previous record where possible.
- Insertion either uses an empty record or splits a larger record.
- File type byte is populated only when the filesystem has `EXT2_FEATURE_INCOMPAT_FILETYPE`.

Concurrency and consistency:
- Directory changes use folio locking and `__block_write_begin()` through `ext2_prepare_chunk()`.
- `ext2_commit_chunk()` increments inode version, completes write, extends `i_size` if needed, and unlocks the folio.
- Readdir tracks an inode version cookie in `file->private_data`; if the directory changed, offsets are revalidated to record boundaries.
- Directory sync behavior writes and waits on directory mapping and inode metadata.

Error handling:
- Corrupt zero-length entries cause `-EIO`.
- Bad directory layout reports `ext2_error()`.
- Entry lookup returns `-ENOENT` when absent.
- Duplicate insertion returns `-EEXIST`.

Research notes:
- This file deliberately contains directory layout knowledge, while `namei.c` contains VFS operation glue.
- It is an important correctness boundary because ext2 directory records are mutable variable-length records inside ordinary file data blocks.
