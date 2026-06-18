# File Research: sources/os/linux/linux/fs/ufs/dir.c

Purpose: UFS directory page-cache validation, lookup, mutation, and readdir support.

Key behavior:
- `ufs_check_folio()` validates directory record lengths, alignment, chunk boundaries, name length, and inode bounds before marking a folio checked.
- `ufs_get_folio()` reads, maps, and validates a directory folio.
- `ufs_find_entry()` searches from the cached start page and returns a mapped folio plus entry.
- `ufs_add_link()` finds free/splittable space or extends the directory, writes a new directory entry, updates timestamps, and syncs when needed.
- `ufs_set_link()` changes an existing entry to point to another inode.
- `ufs_delete_entry()` deletes by merging with the previous entry within the directory block or zeroing the target inode.
- `ufs_make_empty()` creates `.` and `..` in a new directory.
- `ufs_empty_dir()` verifies only `.` and `..` entries exist.
- `ufs_readdir()` emits entries and revalidates offsets when directory version changes.
- Directory file operations install open/release cookie management, `iterate_shared`, `llseek`, `fsync`, and lease handling.

Integration:
- Used by UFS namespace operations in `namei.c` and inode write path through `ufs_prepare_chunk()`.
- Depends on `ufs_aops` from `inode.c`, UFS endian helpers, and superblock directory block size.

Risks and invariants:
- Directory entries may not span directory chunks.
- Readdir stores an i_version cookie in `file->private_data` for offset validation.
- Folio map/unmap ownership is important; returned entries remain mapped until caller releases the folio.
