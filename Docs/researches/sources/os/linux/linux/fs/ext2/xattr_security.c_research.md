# File Research: sources/os/linux/linux/fs/ext2/xattr_security.c

## Purpose
Implements ext2 `security.*` extended attribute support for Linux security modules.

## Main Responsibilities
- Defines get/set handler wrappers around `ext2_xattr_get()` and `ext2_xattr_set()` using `EXT2_XATTR_INDEX_SECURITY`.
- Implements `ext2_initxattrs()` to write all security xattrs supplied during inode initialization.
- `ext2_init_security()` delegates to `security_inode_init_security()`.

## Integration Points
Connects ext2 inode creation to LSM-provided labels such as SELinux contexts. Exposes `ext2_xattr_security_handler` with `XATTR_SECURITY_PREFIX`.

## Risks and Edge Cases
Initialization stops on the first failed xattr write. Security labeling depends on ext2 xattr support and available EA block space.
