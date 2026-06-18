# File Research: sources/os/linux/linux-stable/fs/nilfs2/dir.c

## Summary
Implements NILFS directory entry operations. The code is ext2-derived and manages block-sized directory chunks through the page cache.

## Main Responsibilities
- Converts directory record lengths between disk and memory formats.
- Validates directory folios before use.
- Iterates directory entries for readdir.
- Finds entries by name.
- Finds and validates the `..` entry.
- Adds, updates, deletes, and creates directory entries.
- Checks whether a directory is empty.
- Defines directory file operations.

## Important Behavior
Directory records cannot cross filesystem block-sized chunks. Folio validation checks chunk-size alignment, minimal record size, name length fit, page/chunk boundaries, zero-length entries, and disallowed private inode numbers. Validated folios are marked checked.

`nilfs_find_entry()` starts searching from `i_dir_start_lookup` and wraps around the directory, caching the successful folio index for later lookups. `nilfs_readdir()` advances `ctx->pos` by record lengths and emits VFS file types from NILFS directory file types.

`nilfs_add_link()` searches existing folios and one possible extension folio, splitting an existing record if needed or using a free record. Changes are prepared through `__block_write_begin()` and committed with `block_write_end()`, then the directory is marked dirty.

`nilfs_delete_entry()` merges the removed entry into the previous record when available. `nilfs_make_empty()` creates the initial `.` and `..` entries in one chunk. `nilfs_empty_dir()` permits only valid `.` and `..` records with inode references.

## Risks
The code depends on folio kmap pointers remaining valid until `folio_release_kmap()`. Some error paths use pointer variables that have been advanced for scanning, so the caller must rely on the helper's intended release pattern. Directory corruption is reported with filesystem errors and generally returns `-EIO` or a false empty-dir result.
