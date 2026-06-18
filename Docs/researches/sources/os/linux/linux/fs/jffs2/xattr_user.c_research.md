# File Research: sources/os/linux/linux/fs/jffs2/xattr_user.c

## Purpose
Provides the JFFS2 user xattr handler for the Linux xattr framework.

## Key Functions
- `jffs2_user_getxattr()` calls `do_jffs2_getxattr()` with `JFFS2_XPREFIX_USER`.
- `jffs2_user_setxattr()` calls `do_jffs2_setxattr()` with `JFFS2_XPREFIX_USER`.

## Exported Object
- `jffs2_user_xattr_handler` uses `XATTR_USER_PREFIX` and the user get/set delegates.

## Dependencies
- Includes Linux fs/xattr/JFFS2/MTD headers and JFFS2 `nodelist.h`.
- Depends on core xattr operations implemented in `xattr.c`.
