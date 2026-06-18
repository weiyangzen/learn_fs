# File Research: sources/local-fs/btrfs-linux/fs/btrfs/messages.h

## Purpose

Defines Btrfs logging macros, assertion behavior, error-handling wrappers, panic wrappers, and 32-bit limit declarations.

## Main Contents

- Severity macros: `btrfs_crit`, `btrfs_err`, `btrfs_warn`, `btrfs_info`, plus ratelimited variants.
- Dynamic-debug aware `btrfs_debug` macros.
- RCU-wrapped printk helpers.
- `ASSERT()` implementation under `CONFIG_BTRFS_ASSERT`, including optional format strings.
- `DEBUG_WARN()` under `CONFIG_BTRFS_DEBUG`.
- `btrfs_handle_fs_error()` and `btrfs_panic()` wrappers that capture function and line.
- 32-bit page-cache logical address limit constants and declarations.

## Key Contract

`btrfs_panic()` calls `__btrfs_panic()` and then `BUG()` unless the helper panics first due to mount options.
