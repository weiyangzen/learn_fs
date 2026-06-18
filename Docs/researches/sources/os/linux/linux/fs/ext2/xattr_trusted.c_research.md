# File Research: sources/os/linux/linux/fs/ext2/xattr_trusted.c

## Purpose
Implements ext2 `trusted.*` extended attribute namespace handling.

## Main Responsibilities
- Lists trusted attributes only for callers with `CAP_SYS_ADMIN`.
- Routes get/set operations to `ext2_xattr_get()` and `ext2_xattr_set()` with `EXT2_XATTR_INDEX_TRUSTED`.
- Registers `ext2_xattr_trusted_handler` under `XATTR_TRUSTED_PREFIX`.

## Integration Points
Used by the ext2 xattr handler table and VFS xattr dispatch.

## Risks and Edge Cases
Visibility is capability-gated for listing, while actual get/set permission checks are also governed by VFS xattr policy. Storage limitations and corruption behavior are inherited from `xattr.c`.
