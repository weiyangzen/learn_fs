# File Research: sources/local-fs/squashfs-tools/squashfs-tools/xattr_compat.h

Compatibility shim for platforms whose xattr API uses `XATTR_NOFOLLOW`, notably Apple-style xattr calls.

When `XATTR_NOFOLLOW` is defined, maps:
- `lsetxattr(path, name, value, size, flags)` to `setxattr(..., 0, flags | XATTR_NOFOLLOW)`
- `llistxattr(path, buf, size)` to `listxattr(..., XATTR_NOFOLLOW)`
- `lgetxattr(path, name, value, size)` to `getxattr(..., 0, XATTR_NOFOLLOW)`

On platforms already providing Linux-style `l*xattr` calls, this header adds no definitions.
