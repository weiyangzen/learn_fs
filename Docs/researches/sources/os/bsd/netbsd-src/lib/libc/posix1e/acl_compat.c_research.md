# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_compat.c

Symbol-compatibility wrappers for applications built before NFSv4 ACL permission expansion. The old exported symbols forward to current `acl_get_perm_np()`, `acl_add_perm()`, and `acl_delete_perm()`.

`__sym_compat()` binds those wrappers to the `FBSD_1.0` symbol versions.
