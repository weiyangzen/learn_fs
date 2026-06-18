# File Research: sources/os/linux/linux-stable/fs/ext2/xattr_security.c

## Purpose

Implements ext2 `security.*` extended attribute handling and security label initialization.

## Main Responsibilities

- Provides get/set wrappers for the security xattr namespace.
- Initializes new inode security xattrs through Linux Security Module hooks.
- Exposes `ext2_xattr_security_handler`.

## Key Operations

- `ext2_xattr_security_get()` calls `ext2_xattr_get()` with `EXT2_XATTR_INDEX_SECURITY`.
- `ext2_xattr_security_set()` calls `ext2_xattr_set()` with `EXT2_XATTR_INDEX_SECURITY`.
- `ext2_initxattrs()` iterates the xattrs supplied by the security layer and stores each as a security xattr.
- `ext2_init_security()` calls `security_inode_init_security()` with `ext2_initxattrs`.

## Dependencies

- Includes `ext2.h`, `<linux/security.h>`, and `xattr.h`.
- Depends on `CONFIG_EXT2_FS_SECURITY` declarations from `xattr.h`.

## Research Notes

This file is the bridge between ext2’s xattr storage and LSM-managed labels such as SELinux labels. It contains no policy decisions; it stores labels requested by the security framework.
