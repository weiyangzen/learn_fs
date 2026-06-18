# File Research: sources/os/linux/linux-stable/fs/fuse/acl.c

## Purpose
Implements POSIX ACL get/set support for FUSE in terms of xattr operations and FUSE connection capabilities.

## Key Interfaces
- `fuse_get_acl()` handles VFS dentry-based ACL retrieval.
- `fuse_get_inode_acl()` supports inode ACL checks, including RCU rejection with `-ECHILD`.
- `fuse_set_acl()` serializes ACLs to xattr format, sets or removes ACL xattrs, and invalidates cached ACL/attribute state when appropriate.

## Design Notes
`__fuse_get_acl()` reads `system.posix_acl_access` or `system.posix_acl_default` through `fuse_getxattr()` into a page-sized buffer and converts it with `posix_acl_from_xattr()`. The helper returns `NULL` for absent ACLs and maps `-ERANGE` to `-E2BIG`.

Backward compatibility is explicit: daemons without `FUSE_POSIX_ACL` can still expose ACL xattrs without kernel permission-check participation, especially outside `init_user_ns`.

## Dependencies
Uses FUSE xattr helpers, POSIX ACL conversion helpers, user namespace mapping, `forget_all_cached_acls()`, and `fuse_invalidate_attr()`.

## Research Notes
When setting ACLs under true POSIX ACL support, the code may request setgid stripping with `FUSE_SETXATTR_ACL_KILL_SGID` unless the caller is in the inode group or capable.
