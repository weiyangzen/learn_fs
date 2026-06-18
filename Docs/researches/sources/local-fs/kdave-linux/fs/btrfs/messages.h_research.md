# File Research: sources/local-fs/kdave-linux/fs/btrfs/messages.h

## Purpose

`messages.h` defines Btrfs logging macros, assertion behavior, filesystem error/panic interfaces, and 32-bit address-limit constants.

## Logging API

The header defines severity wrappers:

- `btrfs_crit()`
- `btrfs_err()`
- `btrfs_warn()`
- `btrfs_info()`

and ratelimited variants. With dynamic debug, `btrfs_debug()` and `btrfs_debug_rl()` route through `_dynamic_func_call_no_desc()`. Without debug support, debug macros compile to no-ops while still consuming `fs_info`.

When `CONFIG_PRINTK` is disabled, print macros use `btrfs_no_printk()`.

## Assertions

Under `CONFIG_BTRFS_ASSERT`, `ASSERT()` verifies a condition and supports optional printk-style messages. It prints the failed condition, file, line, and optional format text, then calls `BUG()`. Without assertions, it uses `BUILD_BUG_ON_INVALID(cond)` to type-check expressions without generating runtime code.

`DEBUG_WARN()` maps to `WARN()` only under `CONFIG_BTRFS_DEBUG`.

## Error/Panic Interfaces

The header declares:

- `__btrfs_handle_fs_error()`
- `btrfs_decode_error()`
- `__btrfs_panic()`

and wraps them with `btrfs_handle_fs_error()` and `btrfs_panic()` macros that inject `__func__` and `__LINE__`.

## 32-bit Limits

On 32-bit builds, it defines `BTRFS_32BIT_MAX_FILE_SIZE`, an early warning threshold, and declarations for warning/error emitters.

## Integration Notes

This header is widely included by Btrfs code and controls how assertions and diagnostics behave across debug, printk, and production configurations. Format-string validation in `ASSERT()` reduces risk of broken assertion messages.
