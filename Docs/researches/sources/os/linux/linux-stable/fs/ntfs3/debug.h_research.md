# File Research: sources/os/linux/linux-stable/fs/ntfs3/debug.h

This header defines ntfs3 debug/logging support and common pointer arithmetic macros.

Main responsibilities:
- Defines `Add2Ptr(P, I)` and `PtrOffset(B, O)` if not already defined.
- Declares `ntfs_printk()` and `ntfs_inode_printk()` with printf format checking when `CONFIG_PRINTK` is enabled.
- Provides no-op inline versions when printk support is disabled.
- Defines log-level wrappers: `ntfs_err`, `ntfs_warn`, `ntfs_info`, `ntfs_notice`, `ntfs_inode_err`, and `ntfs_inode_warn`.

Research notes:
- The pointer helpers are heavily used throughout ntfs3 metadata parsing for packed on-disk records.
- Logging macros centralize superblock- and inode-context messages while preserving kernel log levels.
