# File Research: sources/local-fs/btrfs-linux/fs/btrfs/messages.c

## Purpose

Implements Btrfs logging, error decoding, filesystem error handling, 32-bit address-limit warnings, and fatal panic behavior.

## Main Responsibilities

- Converts fs state bits into compact printable state suffixes.
- Decodes common negative errno values into human-readable strings.
- Handles filesystem errors by recording `fs_error`, stopping discard, marking the superblock readonly, and logging critical context.
- Provides ratelimited per-level `_btrfs_printk()` with device id and state annotations.
- Emits one-time warnings/errors for 32-bit logical address limits.
- Implements `__btrfs_panic()`, honoring the panic-on-fatal-error mount option or falling through for caller `BUG()`.

## Key Behaviors

- `-EROFS` on an already readonly superblock is treated as safe and not escalated.
- Full forced-readonly handling is skipped before `SB_BORN`, avoiding mount-time overreaction.
- Ratelimiting is per log level to prevent low-priority floods from suppressing critical messages.
