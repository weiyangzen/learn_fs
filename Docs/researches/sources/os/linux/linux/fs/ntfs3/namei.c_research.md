# File Research: sources/os/linux/linux/fs/ntfs3/namei.c

## Role

Implements NTFS3 namespace inode and dentry operations: lookup, create, mknod, hardlink, unlink, symlink, mkdir, rmdir, rename, parent lookup for export, and case-insensitive dentry hashing/comparison.

## Name Formatting and Lookup

- `fill_name_de()` converts a Linux `qstr` or existing `cpu_str` UTF-16 name into an NTFS directory entry containing an `ATTR_FILE_NAME`.
- The generated entry uses `FILE_NAME_POSIX`, aligned entry sizing, and key size equal to the full filename attribute size.
- `ntfs_lookup()` converts the dentry name to UTF-16, locks the directory, calls `dir_search_u()`, rejects malformed non-base-record inodes with null `i_op`, and returns `d_splice_alias()`.

## Creation Operations

- `ntfs_create()` delegates regular-file creation to `ntfs_create_inode()`.
- `ntfs_mknod()` delegates special-file creation.
- `ntfs_symlink()` creates an NTFS reparse-point symlink.
- `ntfs_mkdir()` creates a directory through `ntfs_create_inode()` and returns an error dentry pointer on failure.

## Link, Unlink, and Remove

- `ntfs_link()` rejects directory hardlinks and link-count overflow, locks parent and target inode, increments Linux link state before attempting `ntfs_link_inode()`, and rolls back on failure.
- `ntfs_unlink()` checks bad inode and forced shutdown, locks the directory, and delegates to `ntfs_unlink_inode()`.
- `ntfs_rmdir()` follows the same wrapper pattern as unlink; emptiness is checked in `ntfs_unlink_inode()`.

## Rename

`ntfs_rename()` supports `RENAME_NOREPLACE` only:

- no-ops same-name same-directory renames;
- rejects metadata-file renames;
- unlinks an existing target before renaming;
- allocates a PATH_MAX work buffer containing old and new directory entries;
- locks old directory, target inode, and new directory when distinct;
- delegates metadata changes to `ni_rename()`;
- updates timestamps, dirty state, and dirsync writes.

## Parent and Dentry Operations

- `ntfs3_get_parent()` scans `ATTR_NAME` attributes and returns an alias for the parent reference stored in `fname->home`.
- `ntfs_d_hash()` hashes ASCII names quickly using uppercase characters, falling back to UTF-16 conversion and NTFS upcase-table hashing for non-ASCII names.
- `ntfs_d_compare()` compares ASCII names case-insensitively fast, then falls back to UTF-16 conversion and `ntfs_cmp_names_cpu()`.

## Exported Operations

- `ntfs_dir_inode_operations` wires lookup/create/link/unlink/symlink/mkdir/rmdir/mknod/rename plus ACL, setattr/getattr, listxattr, fiemap, and fileattr_get.
- `ntfs_special_inode_operations` provides setattr/getattr/listxattr and ACL operations.
- `ntfs_dentry_ops` provides NTFS-aware hash and compare functions.

## Dependencies

Uses Linux VFS, NLS, ctype, and POSIX ACL headers plus NTFS3 directory, inode, xattr, ACL, Unicode conversion, and rename helpers.

## Research Notes

This file is the Linux namespace front-end for NTFS3. Most heavy metadata work is delegated to `inode.c`, `frecord.c`, and `index.c`; this layer focuses on VFS locking/order, name conversion, casefold-compatible dentry behavior, and operation-table wiring.
