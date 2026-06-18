# File Research: sources/os/linux/linux-stable/fs/ext4/xattr_user.c

## Purpose
Provides ext4 handling for `user.*` extended attributes.

## Main Components
- Listing, get, and set are gated by the `XATTR_USER` mount option.
- Unsupported mounts return `-EOPNOTSUPP`.
- Storage operations delegate to `ext4_xattr_get()` and `ext4_xattr_set()` with `EXT4_XATTR_INDEX_USER`.

## Exported Interface
Defines `ext4_xattr_user_handler` with `XATTR_USER_PREFIX`.

## Research Notes
This file is a policy shim for user namespace availability; all layout and journaling behavior lives in `xattr.c`.
