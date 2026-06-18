# File Research: sources/os/linux/linux-stable/fs/ext2/xattr_trusted.c

## Purpose

Implements ext2 `trusted.*` extended attribute handling.

## Main Responsibilities

- Restricts listing of trusted xattrs to callers with `CAP_SYS_ADMIN`.
- Provides get/set wrappers for the trusted xattr namespace.
- Exposes `ext2_xattr_trusted_handler`.

## Key Operations

- `ext2_xattr_trusted_list()` returns `capable(CAP_SYS_ADMIN)`.
- `ext2_xattr_trusted_get()` calls `ext2_xattr_get()` with `EXT2_XATTR_INDEX_TRUSTED`.
- `ext2_xattr_trusted_set()` calls `ext2_xattr_set()` with `EXT2_XATTR_INDEX_TRUSTED`.

## Dependencies

- Includes `ext2.h` and `xattr.h`.
- Uses Linux xattr handler prefix `XATTR_TRUSTED_PREFIX`.

## Research Notes

Trusted xattrs are privileged metadata. This file delegates persistence to the generic ext2 xattr block code and only adds namespace selection plus list permission filtering.
