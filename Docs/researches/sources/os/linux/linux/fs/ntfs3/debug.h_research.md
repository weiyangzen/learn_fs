# File Research: sources/os/linux/linux/fs/ntfs3/debug.h

Read coverage: complete file, 55 lines.

This header defines ntfs3 debug/logging helpers.

Key contents:
- Declares `struct super_block` and `struct inode`.
- Defines pointer arithmetic helpers `Add2Ptr()` and `PtrOffset()` if not already defined.
- If `CONFIG_PRINTK` is enabled, declares `ntfs_printk()` and `ntfs_inode_printk()` with printf format checking.
- Otherwise provides empty inline stubs.
- Defines logging macros: `ntfs_err`, `ntfs_warn`, `ntfs_info`, `ntfs_notice`, `ntfs_inode_err`, and `ntfs_inode_warn`.

Integration:
- Included across ntfs3 source files for diagnostics and pointer helpers.
- Centralizes message severity prefixes.

Risk:
- `Add2Ptr()` / `PtrOffset()` are raw pointer arithmetic helpers used extensively for on-disk structure parsing; callers must validate bounds.
