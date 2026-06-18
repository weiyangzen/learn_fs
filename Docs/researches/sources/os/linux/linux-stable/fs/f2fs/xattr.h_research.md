# File Research: sources/os/linux/linux-stable/fs/f2fs/xattr.h

## Purpose
`xattr.h` defines F2FS on-disk xattr structures, constants, layout macros, handler declarations, and conditional stubs.

## Main Contents
- Magic and limits:
  - `F2FS_XATTR_MAGIC`
  - `F2FS_XATTR_REFCOUNT_MAX`
- Xattr namespace indexes:
  - user, POSIX ACL access/default, trusted, lustre, security, advise, encryption, verity.
- Reserved internal names:
  - encryption context name `"c"`
  - verity descriptor-location name `"v"`
  - `system.advise`
- On-disk structures:
  - `struct f2fs_xattr_header`
  - `struct f2fs_xattr_entry`
- Layout helpers:
  - `XATTR_HDR`
  - `XATTR_ENTRY`
  - `XATTR_FIRST_ENTRY`
  - `XATTR_ALIGN`
  - `ENTRY_SIZE`
  - `XATTR_NEXT_ENTRY`
  - `IS_XATTR_LAST_ENTRY`
  - `list_for_each_xattr`
  - `XATTR_SIZE`
  - `MIN_OFFSET`
  - `MAX_VALUE_LEN`

## Layout Contract
The header documents that F2FS uses inline xattr space plus one xattr block. Entries are packed after the header, with values stored immediately after names and with a zero terminator marking the end. `MIN_OFFSET` defines the maximum usable xattr region before the node footer.

## Conditional API
When `CONFIG_F2FS_FS_XATTR` is enabled, this header declares the real xattr handlers and operations. Otherwise it supplies `NULL` handlers and `-EOPNOTSUPP` stubs for get/set, plus no-op cache lifecycle functions.

When `CONFIG_F2FS_FS_SECURITY` is disabled, `f2fs_init_security` is a no-op stub.

## Dependencies
- Consumed by `xattr.c`, `super.c`, and `verity.c`.
- Depends on inode-specific helpers/macros from the broader F2FS headers for inline xattr sizing and inode state.
