# File Research: sources/os/linux/linux/fs/btrfs/messages.h

This header defines Btrfs logging macros, assertion behavior, filesystem error handling entry points, panic helpers, and 32-bit limit warning declarations.

Logging API:
- `btrfs_crit()`, `btrfs_err()`, `btrfs_warn()`, and `btrfs_info()` log with filesystem/device context under RCU.
- `btrfs_*_rl()` variants add per-call-site rate limiting.
- `btrfs_debug()` and `btrfs_debug_rl()` integrate with dynamic debug or compile out in non-debug builds.
- When printk is unavailable, logging expands to no-op stubs.

Assertions and debug:
- `ASSERT()` is active under `CONFIG_BTRFS_ASSERT`; it supports optional format strings and BUGs on failure.
- When assertions are disabled, the condition is still compile-checked without generated runtime code.
- `DEBUG_WARN()` emits only for `CONFIG_BTRFS_DEBUG`.

Error and panic API:
- `btrfs_handle_fs_error()` wraps `__btrfs_handle_fs_error()` with function and line metadata.
- `btrfs_decode_error()` exposes errno-to-string mapping.
- `btrfs_panic()` wraps `__btrfs_panic()` and then BUGs unless the panic path terminates first.

32-bit support:
- Defines `BTRFS_32BIT_MAX_FILE_SIZE` and early warning threshold for logical address limits.
- Declares warning/error helpers on 32-bit builds.

Design notes:
- The macros centralize Btrfs log formatting so callers do not manually assemble device and filesystem state context.
- The assertion macro includes format-string compile checking to avoid malformed debug messages.
