# File Research: sources/os/linux/linux-stable/fs/statfs.c

## Summary
Implements VFS filesystem-stat retrieval and the `statfs`, `fstatfs`, `statfs64`, `fstatfs64`, and `ustat` syscall families, including compat variants.

## Key APIs
- `vfs_get_fsid()`.
- `vfs_statfs()`.
- `user_statfs()`.
- `fd_statfs()`.

## Important Behavior
`statfs_by_dentry()` zeroes a `kstatfs`, performs `security_sb_statfs()`, calls the filesystem `statfs` super operation, and defaults `f_frsize` to `f_bsize` when the filesystem leaves it unset.

`vfs_statfs()` adds `f_flags` derived from mount flags and superblock flags. Path-based lookup follows symlinks and automounts, retrying with revalidation on ESTALE. FD-based lookup stats the file path.

Native and 64-bit copy helpers convert `kstatfs` to user ABI structures and perform overflow checks for 32-bit-sized fields. `ustat` locates a superblock by device and returns legacy free block/inode counts. Compat syscall handlers mirror the native logic into compat structures.

## Risks
Like `stat.c`, this file is syscall ABI-sensitive. Overflow behavior and compat layout handling must remain consistent with architecture expectations, and all user copies must return `-EFAULT` on failure.
