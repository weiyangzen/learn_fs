# File Research: sources/os/linux/linux-stable/fs/ufs/dir.c

## Summary
Implements UFS directory page-cache validation, lookup, readdir, link insertion, entry replacement/deletion, empty-directory creation, empty-directory checks, and directory file operations.

## Main Responsibilities
- Validates directory folios for record length, alignment, name length, chunk boundaries, and inode range.
- Finds entries by name with an offset cache in `i_dir_start_lookup`.
- Adds links by reusing empty entries, splitting oversized records, or extending the directory.
- Updates existing directory entries through `ufs_set_link()`.
- Iterates directories with version-based revalidation for stable seeking.
- Deletes entries by merging record length into the previous entry within a directory block.
- Creates `.` and `..` entries for new directories.
- Checks whether a directory contains only `.` and `..`.

## Important Behavior
Directory mutation uses `ufs_prepare_chunk()` and `ufs_commit_chunk()` so page-cache writes go through UFS block mapping and update inode version. Directory sync mode flushes mapping and inode metadata.

`ufs_readdir()` stores an inode version in `file->private_data` and validates the seek offset when the directory has changed.

## Risks
Directory records must not span configured directory block chunks. Corrupt `d_reclen == 0` is treated as I/O corruption to avoid infinite loops.
