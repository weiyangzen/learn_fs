# File Research: sources/os/linux/linux/fs/minix/dir.c

## Purpose
`dir.c` implements Minix directory file operations and directory-entry manipulation for lookup, iteration, creation, deletion, emptiness checks, parent lookup, and link updates.

## Main Responsibilities
- Provides `minix_dir_operations` with llseek, generic read-dir fallback, shared iteration, and fsync.
- Iterates directory entries for `readdir`.
- Finds a directory entry matching a dentry name.
- Adds a new directory link, expanding the directory when needed.
- Deletes or updates an existing directory entry.
- Initializes `.` and `..` entries for a new directory.
- Checks whether a directory is empty except for `.` and `..`.
- Reads the `..` entry and resolves an inode number by name.

## Key Functions
- `minix_last_byte()`: returns the valid byte limit within a page for the directory size.
- `dir_commit_chunk()`: completes a write chunk, extends `i_size` if needed, marks inode dirty, and unlocks the folio.
- `minix_handle_dirsync()`: writes and syncs directory metadata for synchronous directory updates.
- `dir_get_folio()`: reads a directory folio and maps it locally.
- `minix_next_entry()`: advances by filesystem-specific directory record size.
- `minix_readdir()`: aligns `ctx->pos`, scans mapped folios, handles v1/v2 versus v3 entry formats, and emits nonzero inode entries.
- `minix_find_entry()`: scans pages for a matching name and returns a mapped entry pointer that the caller must release.
- `minix_add_link()`: finds an empty slot or end-of-directory slot, prepares the chunk, writes name/inode, commits, updates times, and syncs if required.
- `minix_delete_entry()`: zeros the inode field in an entry and updates directory metadata.
- `minix_make_empty()`: creates initial `.` and `..` entries in a new directory.
- `minix_empty_dir()`: scans for entries other than valid `.`/`..`.
- `minix_set_link()`: updates an entry to point to a new inode.
- `minix_dotdot()`: returns the second directory entry from page zero.
- `minix_inode_by_name()`: finds an entry and returns its inode number.

## Integration Points
- Uses Minix superblock fields `s_dirsize`, `s_namelen`, and `s_version`.
- Uses folio/page-cache and buffer-head write preparation helpers.
- Called by Minix namei operations for lookup/create/link/unlink/rename/rmdir.
- Uses `minix_fsync()` from `file.c`.

## Concurrency and Lifetime Notes
- Directory modification locks the target folio while preparing and committing chunks.
- Mapped folios must be released with `folio_release_kmap()`, and freshly grabbed folios are put with `folio_put()`.
- `dir_commit_chunk()` unlocks the folio after `block_write_end()`.
- Directory timestamp updates use current ctime/mtime helpers and mark the inode dirty.

## Risks and Edge Cases
- Name matching permits exact full-length names and rejects shorter buffer names with trailing data.
- `minix_add_link()` scans through `n <= npages`, intentionally allowing expansion beyond current size.
- Directory format differences are handled repeatedly in hot loops, with v3 using 32-bit inode fields and older formats using `minix_dir_entry`.
- `minix_empty_dir()` validates that `.` points to the directory itself and that entries with prefix `.` but extra characters are not treated as empty.
