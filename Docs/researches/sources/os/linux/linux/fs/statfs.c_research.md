# File Research: sources/os/linux/linux/fs/statfs.c

Implements filesystem-stat query plumbing and statfs-family syscalls.

`statfs_by_dentry()` calls the filesystem `statfs` operation after LSM permission checks and fills default fragment size. `vfs_statfs()` adds mount/superblock-derived flags such as read-only, nosuid, nodev, noexec, noatime, relatime, nosymfollow, synchronous, and mandlock.

Path and fd helpers back `statfs`, `statfs64`, `fstatfs`, and `fstatfs64`, including size validation and user-copy translation with overflow checks.

Also implements legacy `ustat` by device and compat statfs/statfs64/ustat conversions under `CONFIG_COMPAT`.
