# File Research: sources/os/linux/linux/fs/affs/namei.c

Purpose: implements AFFS VFS name operations, name hashing/comparison, lookup, create/remove/link/symlink/rename, and export operations.

Key interfaces:
- Dentry ops: `affs_dentry_operations`, `affs_intl_dentry_operations`.
- `affs_lookup()`, `affs_create()`, `affs_mkdir()`, `affs_unlink()`, `affs_rmdir()`, `affs_link()`, `affs_symlink()`, `affs_rename2()`.
- Export ops: `affs_export_ops`.

Implementation notes:
- Supports normal DOS and international uppercase folding for case-insensitive hashing/comparison.
- Names are validated with `affs_check_name()` and may be truncated to `AFFSNAMEMAX` unless no-truncate mount behavior applies.
- `affs_find_entry()` hashes the target name to a parent bucket and walks AFFS hash chains, matching with AFFS case folding.
- `affs_lookup()` stores the real header block in `d_fsdata`; file links resolve through `original`.
- Create/mkdir allocate a new inode, set mode/protection, assign ops, and call `affs_add_entry()`.
- Symlink creation rewrites Unix absolute paths into AFFS volume-relative syntax using `s_volume`, strips redundant slashes, and handles `.`/`..` path patterns.
- Rename removes the old hash entry, rewrites the name, and inserts into the new parent; exchange rename removes both entries then reinserts swapped names.

Dependencies:
- Uses AFFS hash/table helpers, inode allocation, remove/insert hash helpers, symlink aops, and exportfs generic inode-handle helpers.

Edge cases:
- Rename has a TODO about restoring the old directory entry if insertion into the new directory fails.
- Directory hard links are commented out/disabled in lookup.
- NFS export inode lookup rejects invalid block numbers with `-ESTALE`.
