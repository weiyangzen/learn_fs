# File Research: sources/os/linux/linux/fs/ext2/xattr_user.c

## Purpose
Implements ext2 `user.*` extended attribute namespace handling.

## Main Responsibilities
- Lists user attributes only when the `XATTR_USER` mount option is enabled.
- Rejects get/set with `-EOPNOTSUPP` when `XATTR_USER` is disabled.
- Routes enabled get/set operations to `ext2_xattr_get()` and `ext2_xattr_set()` using `EXT2_XATTR_INDEX_USER`.
- Registers `ext2_xattr_user_handler` under `XATTR_USER_PREFIX`.

## Integration Points
Driven by mount options parsed in `super.c` and used by VFS xattr dispatch.

## Risks and Edge Cases
User xattrs can be present on disk but hidden/inaccessible if the mount option is disabled.
