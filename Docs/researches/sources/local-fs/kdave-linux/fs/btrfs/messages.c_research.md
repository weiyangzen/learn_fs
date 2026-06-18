# File Research: sources/local-fs/kdave-linux/fs/btrfs/messages.c

## Purpose

`messages.c` implements Btrfs logging, error decoding, filesystem error handling, panic handling, and 32-bit address-limit warnings.

## Major Behavior

When `CONFIG_PRINTK` is enabled, `btrfs_state_to_string()` appends compact filesystem state characters to log messages. It reports error and notable states such as remounting, transaction aborted, log replay aborted, device replacing, skipped checksums, log cleanup error, and emergency shutdown. Read-only state is intentionally not printed as an error state.

`btrfs_decode_error()` maps selected negative errno values to stable human-readable strings, including I/O failure, no space, read-only filesystem, unsupported operation, filesystem corruption, and quota exceeded.

`__btrfs_handle_fs_error()` is the central expected-error path. It ignores `-EROFS` when the superblock is already read-only, logs a critical message with function/line/context, stores `fs_error`, skips full handling before mount completion, stops discard, sets the superblock read-only, and logs forced read-only. It deliberately does not cancel device replace to avoid deadlock risk.

`_btrfs_printk()` formats Btrfs log messages with log-level names and device id, uses per-level ratelimit states, and disables rate limiting under `CONFIG_BTRFS_DEBUG`.

On 32-bit builds, `btrfs_warn_32bit_limit()` and `btrfs_err_32bit_limit()` emit one-time warnings/errors for logical address limits.

`__btrfs_panic()` logs or panics depending on the mount option `PANIC_ON_FATAL_ERROR`; callers then execute `BUG()` through the macro in `messages.h`.

## Dependencies and Integration

The file depends on `fs.h`, `messages.h`, `discard.h`, and `super.h`. It is used across Btrfs for consistent diagnostics and fatal error policy.

## Risk Notes

This is safety-critical because error handling changes filesystem writability. The code avoids repeated noise via ratelimits and one-time flags, but preserves critical errors and forced-readonly transitions.
