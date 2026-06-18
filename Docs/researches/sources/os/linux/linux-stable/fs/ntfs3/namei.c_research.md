# File Research: sources/os/linux/linux-stable/fs/ntfs3/namei.c

## Role

NTFS3 VFS name-operation implementation. This file handles lookup, create, mknod, link, unlink, symlink, mkdir, rmdir, rename, parent lookup for export-style traversal, and dentry hash/compare behavior.

## Key Functions

- `fill_name_de()` formats an NTFS directory entry (`NTFS_DE`) containing an `ATTR_FILE_NAME`, converting Linux names to UTF-16 when needed.
- `ntfs_lookup()` converts the dentry name to UTF-16, searches the directory index, rejects malformed non-base inodes with missing operations, and returns `d_splice_alias()`.
- `ntfs_create()` creates a regular file via `ntfs_create_inode()`.
- `ntfs_mknod()` creates special files via `ntfs_create_inode()`.
- `ntfs_link()` enforces no directory hard links and NTFS link-count limits, then inserts a new NTFS name and instantiates the dentry.
- `ntfs_unlink()` locks the parent directory and delegates to `ntfs_unlink_inode()`.
- `ntfs_symlink()` creates an NTFS reparse-point symlink.
- `ntfs_mkdir()` creates a directory inode.
- `ntfs_rmdir()` delegates to `ntfs_unlink_inode()` after forced-shutdown/bad-inode checks.
- `ntfs_rename()` implements rename with `RENAME_NOREPLACE` support.
  - Rejects unsupported flags and metadata-file renames.
  - Unlinks an existing target first.
  - Builds old/new UTF-16 directory entries.
  - Locks old directory, renamed inode, and new directory in NTFS order.
  - Calls `ni_rename()` and updates timestamps/dirty state.
- `ntfs3_get_parent()` finds a filename attribute and returns an alias for the parent MFT reference.
- `ntfs_d_hash()` computes case-insensitive dentry hashes, using a fast ASCII uppercase path and a UTF-16/upcase-table path for non-ASCII.
- `ntfs_d_compare()` compares dentries case-insensitively, again using a fast ASCII path before falling back to UTF-16 name comparison.

## VFS Exports

- `ntfs_dir_inode_operations` registers directory operations: lookup, create, link, unlink, symlink, mkdir, rmdir, mknod, rename, ACLs, setattr/getattr, xattrs, and fiemap.
- `ntfs_special_inode_operations` registers metadata operations for special files.
- `ntfs_dentry_ops` registers NTFS case-insensitive hash and compare callbacks.

## Research Notes

This file is the VFS entry layer for namespace changes. Actual MFT and index mutations are delegated to inode/index helpers, while `namei.c` focuses on Linux operation semantics, locking order, name conversion, dentry instantiation, and timestamp/dirty bookkeeping.
