# File Research: sources/os/linux/linux-stable/fs/stat.c

## Summary
Implements VFS file metadata retrieval, stat/statx/readlink syscalls, kernel-to-userspace stat structure conversions, compat variants, and inode block-byte accounting helpers.

## Key APIs
- `fill_mg_cmtime()`.
- `generic_fillattr()`, `generic_fill_statx_attr()`, `generic_fill_statx_atomic_writes()`.
- `vfs_getattr_nosec()`, `vfs_getattr()`, `vfs_fstat()`, `vfs_fstatat()`.
- `do_statx()`, `do_statx_fd()`.
- Inode byte accounting helpers: `inode_add_bytes()`, `inode_sub_bytes()`, `inode_get_bytes()`, `inode_set_bytes()`.

## Important Behavior
`generic_fillattr()` fills `struct kstat` from an inode, applying mount idmapping to uid/gid, mgtime handling when enabled, block size/count, and optional i_version change cookies.

`vfs_getattr_nosec()` initializes result masks, sets automount/DAX attributes, calls filesystem `getattr` or `generic_fillattr()`, and lets block device inodes override relevant statx fields through `bdev_statx()`. `vfs_getattr()` adds the LSM `security_inode_getattr()` check.

Path and fd helpers add mount ids, unique mount ids when requested, and mount-root attributes. Filename lookups handle symlink/no-automount flags, `AT_EMPTY_PATH`, and ESTALE retry with `LOOKUP_REVAL`.

The syscall conversion helpers support old stat, new stat, stat64, statx, and compat structures with overflow checks for device numbers, inode numbers, nlink, file sizes, block counts, and block sizes. `readlinkat` performs path lookup without following symlinks, checks LSM readlink permission, touches atime, and calls `vfs_readlink()`.

## Risks
This file is ABI-sensitive. Conversion helpers must preserve historical structure layouts and overflow semantics across architectures. `STATX_CHANGE_COOKIE` and `STATX_ATTR_CHANGE_MONOTONIC` are kept kernel-only by masking them before copying to userspace.
