# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_xattr.h

## Role

Defines JFS extended attribute on-disk list structures, iteration macros, xattr operation prototypes, and security initialization hook.

## Key Definitions

- `struct jfs_ea` describes one attribute: flag, name length, value length, and variable-length null-terminated name followed by value.
- `struct jfs_ea_list` stores overall size plus a variable-length sequence of `struct jfs_ea`.
- `MAXEASIZE` and `MAXEALISTSIZE` are both 65535 bytes.
- `EA_SIZE`, `NEXT_EA`, `FIRST_EA`, `EALIST_SIZE`, and `END_EALIST` provide variable-length list traversal.
- Declares internal set/get/list xattr functions and `jfs_xattr_handlers`.
- If `CONFIG_JFS_SECURITY` is disabled, `jfs_init_security()` is an inline no-op returning 0.

## Design Notes

The format preserves compatibility expectations from OS/2 by keeping the null terminator in the name even though the name length is explicit.
