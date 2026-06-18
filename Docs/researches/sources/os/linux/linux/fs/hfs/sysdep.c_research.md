# File Research: sources/os/linux/linux/fs/hfs/sysdep.c

Purpose: Defines HFS dentry operations and revalidation behavior.

Key functions:
- `hfs_revalidate_dentry()` rejects RCU lookup, accepts negative dentries, and adjusts cached inode times if the system timezone offset changed.
- `hfs_dentry_operations` wires revalidation, casefold hash, and casefold compare callbacks.

Dependencies and integration:
- Uses `hfs_hash_dentry()` and `hfs_compare_dentry()` from `string.c`.
- Uses `HFS_I(inode)->tz_secondswest` to track per-inode timezone adjustment.

Risk notes:
- Time adjustment depends on global `sys_tz`, preserving legacy HFS local-time semantics.
