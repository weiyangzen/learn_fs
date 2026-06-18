# File Research: sources/local-fs/linux-apfs-rw/namei.c

## Purpose
Connects APFS directory lookup, symlink creation, inode operations, and dentry operations to the Linux VFS.

## Main Responsibilities
- Looks up dentries by name through APFS catalog directory records.
- Creates symlinks through the shared `apfs_mkany()` creation path.
- Defines inode operation tables for directories and special files.
- Defines APFS dentry hashing and comparison behavior for case/normalization-insensitive volumes.
- Revalidates negative dentries when create/rename could collide with a normalized equivalent name.

## Key Functions
- `apfs_lookup()`: validates name length, resolves inode number with `apfs_inode_by_name()`, and returns `d_splice_alias()`.
- `apfs_symlink()`: creates APFS symlink inodes with fixed symlink permissions.
- `apfs_dentry_hash()`: hashes normalized Unicode codepoints for normalization-insensitive volumes.
- `apfs_dentry_compare()`: delegates comparison to `apfs_filename_cmp()`.
- `apfs_dentry_revalidate()`: rejects RCU lookup and invalidates relevant negative dentries.

## Dependencies
Uses VFS namei APIs, APFS directory/create/xattr/setattr functions, and Unicode normalization helpers.

## Notes
The file is mostly operation-table wiring, with kernel-version conditionals for symlink and dentry revalidate signatures.
