# File Research: sources/os/linux/linux-stable/fs/xattr.c

## Purpose

This file implements Linux VFS extended attribute handling: resolving xattr namespaces to filesystem handlers, enforcing VFS permission rules, mediating LSM/security hooks, implementing `setxattr/getxattr/listxattr/removexattr` syscall families including `*xattrat`, and providing generic/simple in-memory xattr helpers for pseudo filesystems.

## Main Responsibilities

- Resolves xattr names through `inode->i_sb->s_xattr` handler tables using namespace prefixes.
- Enforces VFS-level xattr access policy:
  - immutable and append-only inodes reject writes;
  - unmapped ids reject writes;
  - `security.*` and `system.*` are delegated to filesystem/security layers;
  - `trusted.*` requires `CAP_SYS_ADMIN`;
  - `user.*` is limited by file type and sticky directory ownership rules.
- Provides exported VFS helpers:
  - `__vfs_setxattr`, `__vfs_setxattr_noperm`, `__vfs_setxattr_locked`, `vfs_setxattr`
  - `__vfs_getxattr`, `vfs_getxattr`, `vfs_getxattr_alloc`
  - `vfs_listxattr`
  - `__vfs_removexattr`, `__vfs_removexattr_locked`, `vfs_removexattr`
- Handles POSIX ACL xattr names by routing syscall paths to ACL helpers rather than normal xattr handlers.
- Implements syscall entry paths for path, symlink-no-follow, fd, empty-path, and `*xattrat` variants.
- Provides generic list helpers and `simple_xattr` rhashtable-backed storage.

## Key Control Flow

- Name resolution:
  - `xattr_resolve_name` checks `IOP_XATTR`, rejects bad inodes, and matches xattr handler prefixes.
  - Handler callbacks receive the suffix after the namespace prefix.
- Set path:
  - syscall imports the name and optionally copies the user value in `setxattr_copy`.
  - `path_setxattrat` dispatches by pathname or fd.
  - `vfs_setxattr` converts file capabilities with `cap_convert_nscap`, locks the inode, performs permission/security/delegation handling, calls the filesystem handler, and emits fsnotify/security post hooks.
- Get path:
  - imports the name, allocates a bounded kernel buffer, calls ACL or VFS get path, copies data to user space, and converts impossible overlarge returns to `-E2BIG`.
  - `security.*` reads first consult LSM via `security_inode_getsecurity`; if unsupported, normal filesystem xattr lookup is used.
- List path:
  - caps user-requested list size at `XATTR_LIST_MAX`, calls `vfs_listxattr`, copies back, and maps impossible oversized results to `-E2BIG`.
- Remove path:
  - routes ACL names to `vfs_remove_acl`, otherwise follows VFS removal with permission/security/delegation handling and post-remove hooks.

## Simple Xattr Facility

The `simple_xattr` helpers implement in-memory xattrs using `rhashtable`:

- `simple_xattrs_init`, `simple_xattrs_alloc`, `simple_xattrs_lazy_alloc`, and `simple_xattrs_free` manage table lifetime.
- `simple_xattr_alloc`, `simple_xattr_free`, and `simple_xattr_free_rcu` manage values and RCU-delayed reclamation.
- `simple_xattr_get` performs RCU-protected lookup.
- `simple_xattr_set` replaces, inserts, removes, or no-ops based on `value`, `XATTR_CREATE`, and `XATTR_REPLACE`.
- `simple_xattr_set_limited` enforces per-inode simple xattr count and total size limits with speculative atomic accounting.
- `simple_xattr_list` merges POSIX ACL, LSM security labels, and stored simple xattrs while hiding `trusted.*` from unprivileged callers and suppressing MAC labels already supplied by LSM.

## Important Invariants and Edge Cases

- Zero-length xattr values are not removals in `__vfs_setxattr`; they are passed as empty values.
- `value == NULL` is removal in the `simple_xattr_set` helper.
- Writes are expected to hold inode serialization; `simple_xattr_set` documents that lookup plus replace/remove is not atomic without external write serialization.
- `simple_xattrs_lazy_alloc` publishes newly allocated tables with store-release semantics and treats remove-without-storage as either `-ENODATA` for replace or a successful no-op.
- `import_xattr_name` rejects empty names and names that fill the fixed buffer without termination as `-ERANGE`.
- The syscall layer supports `AT_EMPTY_PATH` and fd-based operation by passing `pathname == NULL`.

## Dependencies

- VFS inode/path/file helpers, mount write accounting, delegation breaking, audit, fsnotify.
- LSM hooks via `security_inode_*`.
- POSIX ACL helpers via `posix_acl_xattr` and ACL-specific VFS helpers.
- `rhashtable`, RCU, atomic counters, `kvmalloc`/`kvfree`.

## Research Notes

This is the central VFS xattr bridge between user ABI, VFS policy, LSM policy, filesystem xattr handlers, ACL special cases, and generic in-memory xattr storage. The main risk points are permission ordering, delegation retry loops, namespace-specific semantics, user copy bounds, and the write-serialization requirement for simple xattr mutations.
