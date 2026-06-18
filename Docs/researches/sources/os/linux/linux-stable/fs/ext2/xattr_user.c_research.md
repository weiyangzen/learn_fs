# File Research: sources/os/linux/linux-stable/fs/ext2/xattr_user.c

## Purpose

Implements ext2 `user.*` extended attribute handling.

## Main Responsibilities

- Gates user xattr listing, get, and set on the ext2 `XATTR_USER` mount option.
- Provides get/set wrappers for the user xattr namespace.
- Exposes `ext2_xattr_user_handler`.

## Key Operations

- `ext2_xattr_user_list()` checks `test_opt(dentry->d_sb, XATTR_USER)`.
- `ext2_xattr_user_get()` returns `-EOPNOTSUPP` when user xattrs are disabled, otherwise calls `ext2_xattr_get()` with `EXT2_XATTR_INDEX_USER`.
- `ext2_xattr_user_set()` applies the same mount-option gate and calls `ext2_xattr_set()` with `EXT2_XATTR_INDEX_USER`.

## Dependencies

- Includes Linux init/string headers, `ext2.h`, and `xattr.h`.
- Uses `XATTR_USER_PREFIX`.

## Research Notes

The file enforces the mount-level policy for user-visible xattrs. Actual block format, validation, quota, and sharing behavior live in `xattr.c`.
