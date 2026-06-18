# File Research: sources/os/linux/linux-stable/fs/ext4/xattr_security.c

## Purpose
Provides ext4 handling for `security.*` extended attributes and LSM initialization labels.

## Main Components
- Get/set delegate directly to `ext4_xattr_get()` and `ext4_xattr_set()` with `EXT4_XATTR_INDEX_SECURITY`.
- `ext4_initxattrs()` iterates LSM-provided xattrs and writes each with `ext4_xattr_set_handle()` using `XATTR_CREATE`.
- `ext4_init_security()` calls `security_inode_init_security()` with the ext4 setter callback and active journal handle.

## Exported Interface
Defines `ext4_xattr_security_handler` and `ext4_init_security()` when `CONFIG_EXT4_FS_SECURITY` is enabled.

## Research Notes
Security label initialization is journal-handle aware, so new-inode label writes participate in the caller’s ext4 transaction.
