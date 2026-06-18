# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xattrs.c

## Purpose

This file implements VFS FSAL extended attribute operations. It combines a small built-in virtual xattr namespace with native Linux xattr syscalls over file descriptors opened from VFS object handles. The source was read as a complete 641-line file.

## Important APIs, Types, and Functions

Local types are `xattr_getfunc_t`, `xattr_setfunc_t`, and `struct fsal_xattr_def`. The built-in table contains read-only `vfshandle`, implemented by `print_vfshandle`. Helpers include `do_match_type`, `attr_is_read_only`, `xattr_id_to_name`, and `xattr_name_to_id`. Public FSAL methods are `vfs_list_ext_attrs`, `vfs_getextattr_id_by_name`, `vfs_getextattr_value_by_id`, `vfs_getextattr_value`, `vfs_getextattr_value_by_name`, `vfs_setextattr_value`, `vfs_setextattr_value_by_id`, `vfs_remove_extattr_by_id`, and `vfs_remove_extattr_by_name`.

## Control Flow

Listing first emits built-in entries allowed for the object type, then opens the object and appends `flistxattr` names after the cookie. Name-to-id opens the object except for built-ins and searches the native name list; `system.posix_acl_access` is treated as a special synthetic id. Get-by-id dispatches to the built-in getter or resolves a native name then calls `fgetxattr`. Set/remove paths resolve names as needed and call `fsetxattr`/`fremovexattr`.

## State and Persistence Behavior

Built-in `vfshandle` is generated on demand. Native xattrs are persistent filesystem metadata changed by `fsetxattr` and `fremovexattr`. File descriptors are short-lived and closed in each operation unless a caller-supplied fd is used by `vfs_getextattr_value`.

## Dependencies and Integration Points

The code depends on `os/xattr.h`, VFS handle opening, FSAL error conversion, and FSAL xattr cookies. It is wired through `vfs_methods.h` object ops and may be wrapped by MDCACHE xattr methods.

## Risks and Edge Cases

`MAXPATHLEN` fixed buffers can truncate very large xattr lists. Symlinks are mostly not supported because opening by handle is object-type dependent. `vfs_getextattr_value` closes only `local_fd > 0`, so fd zero would not be closed if ever returned. Empty values are stored as one empty byte on set.

## Test Signals

Test listing cookies, small and full result arrays, built-in `vfshandle`, native create/replace/remove, `system.posix_acl_access`, unsupported symlink behavior, ERANGE on short buffers, and error mapping for missing attributes.
