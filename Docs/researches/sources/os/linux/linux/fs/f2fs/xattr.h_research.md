# File Research: sources/os/linux/linux/fs/f2fs/xattr.h

Defines the F2FS on-disk xattr format, xattr namespace constants, layout macros, and exported xattr APIs.

Key behavior:
- Defines `F2FS_XATTR_MAGIC` and `F2FS_XATTR_REFCOUNT_MAX`.
- Defines F2FS xattr indexes:
  - user
  - POSIX ACL access/default
  - trusted
  - Lustre
  - security
  - F2FS advise
  - encryption
  - verity
- Defines compact names for internal encryption and verity xattrs: `"c"` and `"v"`.
- Defines `struct f2fs_xattr_header` with magic, refcount, and reserved fields.
- Defines `struct f2fs_xattr_entry` with name index, name length, little-endian value size, and flexible name/value storage.
- Provides xattr traversal and sizing macros:
  - `XATTR_HDR`, `XATTR_ENTRY`, `XATTR_FIRST_ENTRY`
  - `XATTR_ALIGN`, `ENTRY_SIZE`, `XATTR_NEXT_ENTRY`
  - `IS_XATTR_LAST_ENTRY`, `list_for_each_xattr`
  - `VALID_XATTR_BLOCK_SIZE`, `XATTR_PADDING_SIZE`
  - `XATTR_SIZE`, `MIN_OFFSET`, `MAX_VALUE_LEN`
- Defines inline xattr sizing limits based on inode address space, extra attributes, reserved inline space, and inline dentry minimums.
- Documents the combined layout: inline xattr space plus one xattr block, followed by the node footer.
- Exports xattr handlers and APIs when `CONFIG_F2FS_FS_XATTR` is enabled.
- Provides `-EOPNOTSUPP` stubs and null handler/list definitions when xattrs are disabled.
- Exports `f2fs_init_security()` when `CONFIG_F2FS_FS_SECURITY` is enabled and provides a no-op stub otherwise.

Important interactions:
- `xattr.c` implements the APIs and uses these layout macros for all on-disk parsing/writing.
- `super.c` installs `f2fs_xattr_handlers` into `sb->s_xattr`.
- `verity.c` and fscrypt paths depend on the internal verity/encryption xattr indexes and names.
