# File Research: sources/os/linux/linux-stable/fs/jffs2/xattr_user.c

Registers the `user.*` xattr handler for JFFS2.

Behavior:
- `jffs2_user_getxattr()` forwards reads to `do_jffs2_getxattr()` with `JFFS2_XPREFIX_USER`.
- `jffs2_user_setxattr()` forwards writes/deletes to `do_jffs2_setxattr()` with the user prefix.
- Exports `jffs2_user_xattr_handler` using `XATTR_USER_PREFIX`.

Integration:
- No extra permission/list policy in this file; VFS/xattr core and shared JFFS2 xattr engine handle the work.
