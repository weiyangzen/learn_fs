# File Research: sources/os/linux/linux/fs/stat.c

Implements VFS file-attribute query plumbing and stat-family syscalls.

Core helpers fill `struct kstat` from inodes, including idmapped uid/gid, multigrain ctime/mtime handling, VFS-enforced statx attributes, atomic-write attributes, inode version/change-cookie support, DAX/automount/mount-root flags, block-device overrides, and security checks.

Path/fd wrappers implement `vfs_getattr`, `vfs_fstat`, `vfs_fstatat`, `vfs_statx`, `do_statx`, and `do_statx_fd`, including lookup flag validation, automount/symlink behavior, stale retry, and mount id reporting.

Syscall sections translate `kstat` into old stat, new stat, stat64, statx, readlink/readlinkat, and compat layouts with overflow checks and `copy_to_user()` handling.

The tail implements inode byte accounting helpers for `i_blocks`/`i_bytes`, with locked and caller-locked variants.
