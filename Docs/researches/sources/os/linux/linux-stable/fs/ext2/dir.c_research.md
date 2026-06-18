# File Research: sources/os/linux/linux-stable/fs/ext2/dir.c

## Summary
Implements ext2 linear directory layout handling using folios/pagecache: validation, lookup, readdir, insertion, deletion, empty-directory checks, and directory file operations.

## Main Responsibilities
- Validates ext2 directory entry records in folios.
- Provides directory iteration through `iterate_shared`.
- Finds names and `..` entries.
- Adds, updates, and deletes directory entries.
- Initializes `.` and `..` for new directories.
- Checks whether a directory contains only `.` and `..`.
- Maintains directory version cookies for stable llseek/readdir behavior.

## Key APIs
- `ext2_find_entry()`.
- `ext2_inode_by_name()`.
- `ext2_dotdot()`.
- `ext2_add_link()`.
- `ext2_set_link()`.
- `ext2_delete_entry()`.
- `ext2_make_empty()`.
- `ext2_empty_dir()`.
- `ext2_dir_operations`.

## Important Behavior
Directory records are checked for minimum record size, 4-byte alignment, name length fit, block-boundary containment, and valid inode number. Checked folios are marked with `folio_set_checked()`.

`ext2_add_link()` scans existing records for an empty slot or a splittable record, expanding at `i_size` as needed. `ext2_delete_entry()` merges the deleted record into the previous record when possible. Directory writes clear `EXT2_BTREE_FL`, update times, dirty the inode, and honor dirsync via `filemap_write_and_wait()` plus `sync_inode_metadata()`.

## State and Synchronization
Directory file private data stores an i_version cookie used by `generic_llseek_cookie()` and readdir validation. Folios are kmap-local mapped; successful lookup helpers return mapped folios that callers must release with `folio_release_kmap()`.

## Risks
Directory entry corruption produces `ext2_error()` and often `-EIO`. Correct kmap nesting and release discipline is explicitly documented because lookup helpers return mapped folio pointers.
