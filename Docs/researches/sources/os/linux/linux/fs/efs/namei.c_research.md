# File Research: sources/os/linux/linux/fs/efs/namei.c

Implements EFS lookup and exportfs inode handle resolution.

Key behavior:
- `efs_find_entry()` scans directory blocks and slots for an exact bytewise name match.
- `efs_lookup()` maps the found inode number through `efs_iget()` and splices aliases.
- Provides NFS/export helpers via `generic_fh_to_dentry()` and `generic_fh_to_parent()`.
- `efs_nfs_get_inode()` rejects inode 0 and stale generation mismatches.
- `efs_get_parent()` resolves `..` and returns a dentry alias for the parent inode.

Important interactions:
- Shares the directory parsing format used by `dir.c`.
- Export operations in `super.c` call these helpers.
