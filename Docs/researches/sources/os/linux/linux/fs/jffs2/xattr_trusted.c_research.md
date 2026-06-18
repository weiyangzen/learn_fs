# File Research: sources/os/linux/linux/fs/jffs2/xattr_trusted.c

## Purpose
Provides the JFFS2 trusted xattr handler for the Linux xattr framework.

## Key Functions
- `jffs2_trusted_getxattr()` delegates reads to `do_jffs2_getxattr()` with `JFFS2_XPREFIX_TRUSTED`.
- `jffs2_trusted_setxattr()` delegates writes/removals to `do_jffs2_setxattr()` with `JFFS2_XPREFIX_TRUSTED`.
- `jffs2_trusted_listxattr()` only allows listing trusted attributes for callers with `CAP_SYS_ADMIN`.

## Exported Object
- `jffs2_trusted_xattr_handler` uses `XATTR_TRUSTED_PREFIX`, custom `.list`, and the trusted get/set delegates.

## Dependencies
- Includes Linux fs/xattr/JFFS2/MTD headers and JFFS2 `nodelist.h`.
- Depends on core xattr operations implemented in `xattr.c`.
