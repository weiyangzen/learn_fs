# File Research: sources/os/linux/linux/fs/orangefs/xattr.c

## Role

Implements OrangeFS extended attribute VFS operations, including get/set/remove/list and a small per-inode xattr cache.

## Main Responsibilities

- Filters reserved `system.pvfs2.*` keys from `listxattr()` output.
- Converts Linux `XATTR_CREATE` / `XATTR_REPLACE` flags to OrangeFS protocol flags.
- Uses a 16-bucket simple hash over xattr names for `orangefs_cached_xattr`.
- `orangefs_inode_getxattr()` rejects symlinks, checks name length, consults the cache, issues `ORANGEFS_VFS_OP_GETXATTR`, handles negative caching for missing keys, and copies values to caller buffers.
- `orangefs_inode_setxattr()` validates sizes, treats null zero-size values as remove, issues `ORANGEFS_VFS_OP_SETXATTR`, and invalidates the cached key.
- `orangefs_inode_removexattr()` issues `ORANGEFS_VFS_OP_REMOVEXATTR`, maps missing-key behavior according to replace semantics, and invalidates cache.
- `orangefs_listxattr()` iterates server-side xattr pages using OrangeFS tokens and copies only visible whole keys into the caller buffer.
- Installs a default xattr handler with empty prefix, so handler callbacks receive full names.

## Locking and Caching

All xattr operations use `ORANGEFS_I(inode)->xattr_sem`. Reads take the semaphore shared; set/remove take it exclusive. Positive cache entries are short-lived; missing keys are cached as `length == -1`.

## Edge Cases

`listxattr(size == 0)` returns an upper bound based on returned key count times `ORANGEFS_MAX_XATTR_NAMELEN`, not an exact filtered size. Returned list counts and key lengths are range-checked to guard impossible userspace/server responses.

## Dependencies

Uses OrangeFS upcalls, inode private data, VFS xattr APIs, POSIX ACL xattr names, and OrangeFS xattr protocol limits.

## Research Notes

This file hides OrangeFS-private metadata from generic xattr listing while still allowing direct operations through the full-name handler path.
