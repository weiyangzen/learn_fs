# File Research: sources/os/linux/linux-stable/fs/btrfs/messages.h

## Summary
Defines Btrfs logging macros, assertion macros, filesystem error/panic helpers, and 32-bit address-limit constants.

## Main Contents
- `btrfs_crit()`, `btrfs_err()`, `btrfs_warn()`, `btrfs_info()`.
- Ratelimited variants for each log level.
- Dynamic-debug and debug-build `btrfs_debug()` variants.
- `ASSERT()` with optional printk-style message under `CONFIG_BTRFS_ASSERT`.
- `DEBUG_WARN()`.
- `btrfs_handle_fs_error()` and `btrfs_panic()` wrappers.
- `btrfs_decode_error()` declaration.
- 32-bit maximum file size and early warning threshold constants.

## Important Details
Logging macros wrap `_btrfs_printk()` in RCU read-side protection so device/fs names can be safely printed.

When `CONFIG_PRINTK` is disabled, logging expands to `btrfs_no_printk()` stubs. When assertions are disabled, `ASSERT()` still compile-checks the condition with `BUILD_BUG_ON_INVALID()`.

The assertion macro supports `ASSERT(cond)`, `ASSERT(cond, "msg")`, and `ASSERT(cond, "fmt %d", value)` by splitting the first variadic token from the rest.

## Risks
The macros form a broad diagnostic contract used across Btrfs. Because many branches compile differently depending on `CONFIG_PRINTK`, `CONFIG_DYNAMIC_DEBUG`, `DEBUG`, and `CONFIG_BTRFS_ASSERT`, build coverage across configurations matters.
