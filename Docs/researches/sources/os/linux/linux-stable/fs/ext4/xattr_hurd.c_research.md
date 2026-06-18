# File Research: sources/os/linux/linux-stable/fs/ext4/xattr_hurd.c

## Purpose
Provides the ext4 VFS xattr handler for the GNU/Hurd xattr namespace.

## Main Components
- `ext4_xattr_hurd_list()` exposes Hurd attributes only when the mount has `XATTR_USER`.
- Get/set operations reject unsupported mounts with `-EOPNOTSUPP`.
- Successful operations delegate to `ext4_xattr_get()` and `ext4_xattr_set()` with `EXT4_XATTR_INDEX_HURD`.

## Exported Interface
Defines `ext4_xattr_hurd_handler` with `XATTR_HURD_PREFIX`, list, get, and set callbacks.

## Research Notes
This is a thin namespace adapter; policy is mount-option gated and storage semantics are centralized in `xattr.c`.
