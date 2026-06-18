# File Research: sources/os/linux/linux-stable/fs/exfat/namei.c

This file implements exFAT VFS directory inode operations and dentry operations: lookup, create, unlink, mkdir, rmdir, rename, case-insensitive hashing/comparison, empty-entry allocation, and pathname-to-UTF16 resolution.

Key elements:
- Dentry operations provide case-insensitive hashing/comparison using either NLS tables or UTF-8 decoding, with optional trailing-dot stripping controlled by mount options.
- `exfat_d_revalidate()` validates negative dentries using parent inode version and drops negative creation targets to avoid stale aliases.
- `exfat_search_empty_slot()` and `exfat_find_empty_entry()` find or allocate contiguous directory-entry slots, using `hint_femp` and growing directories by allocating and zeroing clusters.
- `__exfat_resolve_path()` strips trailing periods unless configured otherwise, enforces length limits, converts input names to UTF-16, and rejects lossy/invalid names on creation.
- `exfat_add_entry()` creates a file or directory entry set, allocating initial directory storage unless zero-size directories are enabled.
- `exfat_find()` resolves a child name, reads its entry set, validates size/start cluster/valid size, converts timestamps, and counts subdirectories for directory nlink.
- `exfat_lookup()` builds or reuses inodes by on-disk position and handles alias dentries.
- `exfat_unlink()` and `exfat_rmdir()` mark entry sets deleted, update parent/child metadata, unhash inodes, and set dentry versions.
- Rename support is split into same-directory rename, cross-directory move, and replacement handling. It rewrites entry sets when the new name needs more entries, deletes overwritten targets, frees replaced directory clusters, rehashes moved inodes, and updates nlink counts.
- Exposes `exfat_dir_inode_operations`.

Important dependencies:
- Uses directory entry-set APIs from `dir.c`, name conversion/upcase from `nls.c`, allocation from `fatent.c`, inode construction/hash from `inode.c`, and metadata utilities from `misc.c`.

Failure/edge behavior:
- Rejects unsupported rename flags except `RENAME_NOREPLACE`.
- Checks target directories are empty before replacement/removal.
- Guards against operations on entries whose `ei->dir.dir` is `DIR_DELETED`.
- Directory growth updates `i_size`, `valid_size`, `i_blocks`, and allocation flags immediately.
