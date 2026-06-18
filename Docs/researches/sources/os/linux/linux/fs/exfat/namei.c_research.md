# File Research: sources/os/linux/linux/fs/exfat/namei.c

## Purpose
Implements exFAT namespace operations: dentry hashing/comparison/revalidation, empty-slot search and directory expansion, path/name normalization, lookup, create, unlink, mkdir, rmdir, rename, and move/replace semantics.

## Main Interfaces
- Dentry ops: `exfat_dentry_ops`, `exfat_utf8_dentry_ops`
- Directory inode ops: `exfat_dir_inode_operations`
- Shared helper: `exfat_find_empty_entry`

## Key Data Flow
Dentry operations compute case-insensitive hashes and comparisons using either mounted NLS tables or UTF-8 decoding plus the exFAT upcase table. Negative dentries are versioned against parent `i_version` and dropped for create/rename targets.

Creation flows through `exfat_add_entry()`: resolve VFS name to UTF-16, calculate needed dentry count, find or allocate an empty entry set, optionally allocate a new directory cluster, initialize file/stream/name entries, flush them, and return `exfat_dir_entry` metadata for inode construction.

Lookup calls `exfat_find()` to resolve names using directory hints, read entry metadata, validate sizes/start clusters, count subdirectories for directories, and build/reuse inodes. Unlink/rmdir mark entry sets deleted, update parent timestamps/versions, unhash target inodes, and set dentry version data. Rename either rewrites in-place if the new name fits or allocates/moves entry sets, handles target replacement, frees replaced directory clusters, and updates inode hashes/link counts.

## Dependencies
Uses `dir.c` entry-set helpers, `nls.c` conversion/upcase helpers, allocation helpers, inode construction/hash helpers, VFS dentry/inode APIs, and global `s_lock`.

## Notable Invariants And Risks
- Trailing-dot behavior is mount-option dependent; creation can reject names ending in dots when `keep_last_dots` is enabled.
- exFAT has no native Unix hard links; inode identity follows directory-entry position.
- Rename replacement must handle empty target directories and link-count updates carefully.
