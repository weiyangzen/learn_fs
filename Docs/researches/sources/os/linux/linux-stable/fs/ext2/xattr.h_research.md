# File Research: sources/os/linux/linux-stable/fs/ext2/xattr.h

## Purpose

Defines ext2 xattr on-disk structures, namespace indexes, alignment macros, and public xattr APIs.

## Main Definitions

- `EXT2_XATTR_MAGIC`: magic for xattr blocks.
- `EXT2_XATTR_REFCOUNT_MAX`: maximum shared xattr block references.
- Namespace indexes:
  - `EXT2_XATTR_INDEX_USER`
  - `EXT2_XATTR_INDEX_POSIX_ACL_ACCESS`
  - `EXT2_XATTR_INDEX_POSIX_ACL_DEFAULT`
  - `EXT2_XATTR_INDEX_TRUSTED`
  - `EXT2_XATTR_INDEX_LUSTRE`
  - `EXT2_XATTR_INDEX_SECURITY`
- `struct ext2_xattr_header`: magic, refcount, block count, hash, reserved fields.
- `struct ext2_xattr_entry`: name metadata, value offset/block/size, hash, flexible name.
- Alignment helpers:
  - `EXT2_XATTR_LEN()`
  - `EXT2_XATTR_NEXT()`
  - `EXT2_XATTR_SIZE()`

## Conditional API Surface

When `CONFIG_EXT2_FS_XATTR` is enabled, declares:

- xattr handlers for user/trusted/security namespaces.
- `ext2_listxattr()`.
- `ext2_xattr_get()` and `ext2_xattr_set()`.
- `ext2_xattr_delete_inode()`.
- xattr mbcache create/destroy helpers.
- `ext2_xattr_handlers`.

When xattrs are disabled:

- `ext2_xattr_get()` and `ext2_xattr_set()` return `-EOPNOTSUPP`.
- `ext2_xattr_delete_inode()` and cache destroy are no-ops.
- `ext2_xattr_handlers` and `ext2_listxattr` collapse to `NULL`.

When `CONFIG_EXT2_FS_SECURITY` is disabled:

- `ext2_init_security()` is an inline no-op returning success.

## Dependencies

- Includes `<linux/init.h>` and `<linux/xattr.h>`.
- Forward declares `struct mb_cache`.

## Research Notes

This header is the contract between ext2 inode/superblock code and xattr implementation files. The conditional stubs let non-xattr builds compile away xattr behavior cleanly while preserving call sites.
