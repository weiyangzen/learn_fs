# File Research: sources/os/linux/linux-stable/fs/jffs2/xattr_trusted.c

Registers the `trusted.*` xattr handler for JFFS2.

Behavior:
- `jffs2_trusted_getxattr()` forwards reads to `do_jffs2_getxattr()` with `JFFS2_XPREFIX_TRUSTED`.
- `jffs2_trusted_setxattr()` forwards writes/deletes to `do_jffs2_setxattr()` with the trusted prefix.
- `jffs2_trusted_listxattr()` permits listing only for callers with `CAP_SYS_ADMIN`.
- Exports `jffs2_trusted_xattr_handler` using `XATTR_TRUSTED_PREFIX`.

Integration:
- Thin adapter over the shared implementation in `xattr.c`; policy is only list visibility.
