# File Research: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs_xattr.h

Conditional xattr import interface for mksquashfs. When `XATTR_SUPPORT` and `XATTR_OS_SUPPORT` are enabled, it declares `read_xattrs_from_system()`.

When xattr support is compiled but OS support is absent, it provides a static inline stub returning `0`, meaning no xattrs read from the live filesystem. If `XATTR_SUPPORT` is absent, the header exposes no API.
