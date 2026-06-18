# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_debug.h

Defines JFS debug, assert, and statistics macros.

Key behavior:
- `assert()` always prints a critical BUG message and calls `BUG()` on failure.
- With `CONFIG_JFS_DEBUG`, `ASSERT()` is active and `jfs_info/debug/warn/err` emit printk messages according to `jfsloglevel`.
- Without debug, `ASSERT()` and logging macros compile to no-ops.
- With `CONFIG_JFS_STATISTICS`, declares proc show functions and enables increment/decrement/high-watermark macros; otherwise those are no-ops.
- Defines `PROC_FS_JFS` when procfs and either debug/statistics are enabled.

Risk notes:
- Lowercase `assert()` remains fatal even outside `CONFIG_JFS_DEBUG`, while uppercase `ASSERT()` is gated.
