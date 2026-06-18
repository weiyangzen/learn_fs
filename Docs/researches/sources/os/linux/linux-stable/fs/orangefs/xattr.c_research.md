# File Research: sources/os/linux/linux-stable/fs/orangefs/xattr.c

## Scope

This file implements OrangeFS VFS extended attribute operations: get, set, remove, list, default xattr handler registration, reserved OrangeFS key filtering, create/replace flag translation, and a small per-inode xattr cache.

## Public And Internal APIs Covered

- VFS-facing functions: `orangefs_inode_getxattr()`, `orangefs_inode_setxattr()`, `orangefs_listxattr()`.
- Internal helpers: `is_reserved_key()`, `convert_to_internal_xattr_flags()`, `xattr_key()`, `find_cached_xattr()`, `orangefs_inode_removexattr()`.
- Xattr handler callbacks: `orangefs_xattr_get_default()` and `orangefs_xattr_set_default()`.
- Exports `orangefs_xattr_handlers`.

## Control Flow And Behavior

- `orangefs_inode_getxattr()` rejects symlink xattr reads, validates name length, checks a per-inode hash cache under `xattr_sem`, and supports size probes with `size == 0`.
- Negative cache entries use `length == -1` to return `-ENODATA` without a remote upcall until timeout.
- GETXATTR upcalls copy the key and key length, normalize `-ENOENT` to `-ENODATA`, validate returned value length, copy and zero-fill user buffers, then update or create a short-lived cache entry.
- `orangefs_inode_setxattr()` validates name/value sizes, maps Linux `XATTR_CREATE` / `XATTR_REPLACE` to OrangeFS flags, treats `size == 0 && value == NULL` as removexattr, sends SETXATTR, and invalidates any cached key.
- `orangefs_inode_removexattr()` sends REMOVEXATTR and maps missing-key behavior according to replace semantics.
- `orangefs_listxattr()` iterates using OrangeFS list tokens, validates returned key counts and lengths, filters out internal `system.pvfs2.` keys, and copies only whole keys that fit the caller buffer.
- The default handler uses an empty prefix so VFS passes full xattr names to OrangeFS.

## State And Data Structures

- Per-inode xattr cache is a 16-bucket hash table of `struct orangefs_cached_xattr`, protected by `orangefs_inode->xattr_sem`.
- Cache entries store key, value, length, timeout, and hash node.
- Listxattr upcalls use `ORANGEFS_ITERATE_START` and continue until `ORANGEFS_ITERATE_END`.

## Dependencies

- Uses OrangeFS operation service path for GETXATTR, SETXATTR, LISTXATTR, and REMOVEXATTR.
- Uses Linux xattr and POSIX ACL xattr helpers for flag constants and ACL name recognition.
- Cache storage is freed in `orangefs_free_inode()` from `super.c`.

## Risks And Invariants

- Reserved `system.pvfs2.` keys are intentionally hidden from listxattr output to discourage user modification of OrangeFS internal metadata.
- Returned list counts and lengths are validated defensively; impossible userspace-client responses become `-EIO`.
- The cache timeout code is partially disabled in lookup comments, but callers still check timeout before accepting cached values.
- Write/remove paths must invalidate cached keys under write lock to prevent stale xattr reads.
