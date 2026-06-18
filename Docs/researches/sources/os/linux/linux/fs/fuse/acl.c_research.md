# File Research: sources/os/linux/linux/fs/fuse/acl.c

## Purpose
This file implements POSIX ACL get/set support for FUSE in terms of extended attributes. It preserves compatibility with older FUSE daemons that handled ACL xattrs themselves without advertising `FUSE_POSIX_ACL`.

## Main Definitions
- `__fuse_get_acl()` fetches `system.posix_acl_access` or `system.posix_acl_default` with `fuse_getxattr()` and converts it with `posix_acl_from_xattr()`.
- `fuse_no_acl()` decides whether kernel POSIX ACL interaction should be refused for non-host user namespaces when the daemon lacks POSIX ACL support.
- `fuse_get_acl()` is the dentry-based VFS ACL getter.
- `fuse_get_inode_acl()` is an inode ACL getter used for permission checking, with RCU lookup handling.
- `fuse_set_acl()` serializes ACLs with `posix_acl_to_xattr()`, writes/removes xattrs, optionally requests setgid stripping, and invalidates ACL/attribute caches.

## Control Flow And Behavior
ACL get operations reject RCU mode with `-ECHILD`, reject bad inodes with `-EIO`, return `NULL` when xattr support is absent or the ACL xattr is absent, translate `-ERANGE` to `-E2BIG`, and otherwise propagate errors. ACL type selects the xattr name; unsupported types return `-EOPNOTSUPP`.

`fuse_set_acl()` rejects bad inodes, unsupported setxattr paths, and unsupported ACL types. For non-null ACLs it converts the ACL into xattr bytes, enforces `PAGE_SIZE` maximum, and may set `FUSE_SETXATTR_ACL_KILL_SGID` when the daemon supports POSIX ACLs and the caller lacks group/capability rights. Null ACL removes the xattr.

## Dependencies And Interfaces
The file uses `fuse_getxattr`, `fuse_setxattr`, `fuse_removexattr`, `forget_all_cached_acls`, and `fuse_invalidate_attr` from the FUSE/VFS xattr and cache layers. It also uses user namespace ACL conversion through `fc->user_ns`.

## Concurrency And Safety
The code does per-call allocation and does not manage global state. It respects RCU lookup constraints by returning `-ECHILD` when ACL lookup cannot sleep.

## Research Notes
The compatibility behavior is central: daemons without `FUSE_POSIX_ACL` retain old behavior, especially around VFS permission checking, ACL caching, and setgid stripping.
