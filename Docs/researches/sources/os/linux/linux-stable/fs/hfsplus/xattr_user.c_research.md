# File Research: sources/os/linux/linux-stable/fs/hfsplus/xattr_user.c

## Purpose

Implements the `user.*` HFS+ xattr namespace handler.

## Main Entry Points

- `hfsplus_user_getxattr()`
- `hfsplus_user_setxattr()`
- `hfsplus_xattr_user_handler`

## Control Flow And Dependencies

The callbacks delegate to the core HFS+ get/set helpers with `XATTR_USER_PREFIX`. All storage, namespace formatting, attributes-tree access, and errors are handled in `xattr.c`.

## Risks

No file-local checks are present. Behavior depends on the shared xattr implementation correctly handling HFS+ unsupported states, resource-fork inodes, and attribute-tree availability.
