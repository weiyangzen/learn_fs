# File Research: sources/os/linux/linux-stable/fs/posix_acl.c

## Purpose

Provides generic VFS support for POSIX ACL allocation, caching, validation, permission checks, chmod/create transformations, xattr conversion, and VFS get/set/remove ACL operations.

## Main Responsibilities

- ACL cache handling:
  - `acl_by_type()` selects `inode->i_acl` or `inode->i_default_acl`.
  - `get_cached_acl()` and `get_cached_acl_rcu()` read cached ACLs safely.
  - `set_cached_acl()`, `forget_cached_acl()`, and `forget_all_cached_acls()` update or invalidate caches.
  - `__get_acl()` handles sentinel-based cache fill races and calls filesystem `get_acl` or `get_inode_acl`.
- ACL object lifecycle:
  - `posix_acl_init()`, `posix_acl_alloc()`, and `posix_acl_clone()`.
- ACL validation and mode equivalence:
  - `posix_acl_valid()` validates tag order, permission bits, mask requirements, and uid/gid mappings.
  - `posix_acl_equiv_mode()` determines whether an ACL can be represented by traditional mode bits.
  - `posix_acl_from_mode()` constructs a three-entry ACL from mode bits.
- Permission checking:
  - `posix_acl_permission()` evaluates owner, named user, group object, named group, mask, and other entries with idmapped mount translation.
- ACL create/chmod transformations:
  - `posix_acl_create_masq()` applies create mode/umask semantics.
  - `__posix_acl_chmod_masq()` applies chmod semantics.
  - `__posix_acl_create()`, `__posix_acl_chmod()`, `posix_acl_chmod()`, and `posix_acl_create()` expose these workflows.
- Mode update for set ACL:
  - `posix_acl_update_mode()` updates inode mode bits from ACL and clears setgid when needed.
- Xattr conversion:
  - `posix_acl_from_xattr()` converts on-disk/uapi ACL xattrs into VFS ACLs.
  - `posix_acl_to_xattr()` converts VFS ACLs to filesystem idmapping xattr form.
  - `vfs_posix_acl_to_xattr()` converts to userspace-visible xattr form, accounting for mount idmaps and caller namespace.
- VFS ACL operations:
  - `set_posix_acl()` validates type, directory default ACL rules, ownership, and filesystem support.
  - `vfs_set_acl()` applies idmapped mount translation, VFS write checks, LSM hooks, delegation breaking, filesystem set, fsnotify, and post hooks.
  - `vfs_get_acl()` applies LSM get hook, type checks, symlink rejection, and cache-backed retrieval.
  - `vfs_remove_acl()` applies write checks, LSM remove hook, delegation breaking, filesystem removal, fsnotify, and post hooks.
  - `do_set_acl()` and `do_get_acl()` are xattr syscall-facing helpers.
- Simple filesystem helpers:
  - `simple_set_acl()` updates cached ACLs and ctime/i_version.
  - `simple_acl_create()` initializes inherited ACLs on simple filesystems.
- Legacy xattr handlers:
  - `nop_posix_acl_access` and `nop_posix_acl_default` list POSIX ACL names for older filesystem code.

## Key Data/Control Flow

- The cache sentinel in `__get_acl()` prevents stale cache publication when another thread races with ACL retrieval.
- ACL validity requires canonical entry ordering: user object, optional named users, group object, optional named groups, optional mask, other.
- Named user/group entries require a mask entry.
- Idmapped mounts are applied during permission checks and VFS userspace boundaries, not when caching filesystem ACLs.
- `vfs_set_acl()` mutates the supplied ACL for idmapped mounts before calling filesystem `set_acl()`.

## Security and Correctness Notes

- ACL set/remove paths call `may_write_xattr()` and LSM hooks.
- ACL get path calls `security_inode_get_acl()` but intentionally does not run generic xattr permission checks.
- Default ACLs are only valid on directories; setting a non-null default ACL on non-directories returns `-EACCES`.
- Delegation breaking is retried in set/remove paths.
