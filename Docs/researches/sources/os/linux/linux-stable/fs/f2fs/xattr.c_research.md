# File Research: sources/os/linux/linux-stable/fs/f2fs/xattr.c

## Purpose
`xattr.c` implements F2FS extended attribute handlers, storage lookup, listing, mutation, security initialization, and xattr cache lifecycle.

## Main Responsibilities
- Provides VFS xattr handlers for `user.*`, `trusted.*`, `security.*`, and F2FS `system.advise`.
- Implements F2FS xattr get/list/set operations over inline inode xattr space plus an optional xattr node block.
- Initializes inode security xattrs through LSM callbacks when `CONFIG_F2FS_FS_SECURITY` is enabled.
- Maintains an inline-xattr slab cache for the default inline xattr allocation size.
- Detects malformed xattr entries, marks fsck-needed state, and reports F2FS corruption errors.

## Key Data and Interfaces
- Exported handlers:
  - `f2fs_xattr_user_handler`
  - `f2fs_xattr_trusted_handler`
  - `f2fs_xattr_advise_handler`
  - `f2fs_xattr_security_handler`
  - `f2fs_xattr_handlers[]`
- Exported operations:
  - `f2fs_getxattr`
  - `f2fs_setxattr`
  - `f2fs_listxattr`
  - `f2fs_init_security`
  - `f2fs_init_xattr_cache`
  - `f2fs_destroy_xattr_cache`

## Storage Model
F2FS combines:
- Inline xattr area inside the inode node.
- Optional external xattr node block referenced by `F2FS_I(inode)->i_xattr_nid`.

`read_all_xattrs` builds a temporary contiguous image of inline plus external xattrs. `write_all_xattrs` writes back inline content and allocates/truncates the xattr node block as needed.

## Lookup and Mutation Flow
- `lookup_all_xattrs` reads the required storage, searches inline first, then external storage, and returns the matching entry or `-ENODATA`.
- `f2fs_getxattr` validates name length, locks `i_xattr_sem` when needed, retrieves the entry, checks caller buffer size, and copies the value.
- `f2fs_listxattr` walks all entries, applies handler visibility rules, and emits prefixed names.
- `f2fs_setxattr` checks checkpoint/error state, initializes quota, balances filesystem space, takes the global F2FS op lock plus `i_xattr_sem`, and calls `__f2fs_setxattr`.
- `__f2fs_setxattr` handles create/replace/remove semantics, same-value shortcut, free-space validation, entry compaction, new entry insertion, encrypted inode flag update, directory checkpoint tracking, ctime update, and dirty marking.

## Special Attributes
- `system.advise` maps to `F2FS_I(inode)->i_advise`; only owner/capable callers may modify selected advise bits.
- Encryption context writes mark the inode encrypted.
- Security xattrs are initialized through `security_inode_init_security`.

## Dependencies
- Defines the xattr operations installed by `super.c` via `sb->s_xattr = f2fs_xattr_handlers`.
- Used by `super.c` fscrypt context callbacks and by `verity.c` descriptor-location storage.
- Depends on F2FS node/page helpers from `f2fs.h` and `segment.h`.

## Notable Edge Cases
- Corrupt xattr entry bounds set `SBI_NEED_FSCK` and call `f2fs_handle_error(ERROR_CORRUPTED_XATTR)`.
- If an inline-only inode has corrupted/missing xattr data during set, the code attempts `f2fs_recover_xattr_data`.
- Values larger than `MAX_VALUE_LEN(inode)` are rejected with `-E2BIG`.
- User xattrs honor the `XATTR_USER` mount option; trusted xattrs require `CAP_SYS_ADMIN` to list.
