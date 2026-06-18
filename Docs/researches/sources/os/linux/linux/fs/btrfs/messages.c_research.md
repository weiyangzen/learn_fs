# File Research: sources/os/linux/linux/fs/btrfs/messages.c

This file implements Btrfs logging, error decoding, filesystem error handling, fatal panic handling, and 32-bit address-limit warnings.

Core responsibilities:
- Convert selected errno values to stable human-readable Btrfs error strings.
- Format filesystem state bits into compact log suffixes.
- Print Btrfs messages with device id, log level, state suffix, and rate limiting.
- Handle filesystem errors by recording the error, stopping discard, forcing the filesystem readonly, and logging the transition.
- Panic or BUG on fatal errors depending on mount options.
- Warn once when 32-bit kernels approach or reach logical-address limits.

Key mechanisms:
- `btrfs_state_to_string()` converts notable `fs_state` bits into a short state string; plain readonly is intentionally not treated as an error state.
- `btrfs_decode_error()` maps common Btrfs errors including `-EUCLEAN`, `-EDQUOT`, and `-EROFS`.
- `__btrfs_handle_fs_error()` logs critical error context, stores `fs_error`, skips full handling during mount, and forces a born writable superblock readonly.
- `_btrfs_printk()` uses one ratelimit state per printk level so less important floods do not suppress critical logs.
- `__btrfs_panic()` either calls `panic()` when `PANIC_ON_FATAL_ERROR` is set or logs a critical message before the caller BUGs.
- 32-bit limit helpers set warning/error flags so messages are emitted once.

Important behavior:
- `-EROFS` while the superblock is already readonly is treated as safe and does not force additional error handling.
- Device replace is not canceled during forced readonly to avoid deadlock risk.
- Under `CONFIG_BTRFS_DEBUG`, normal Btrfs printk output is not rate-limited.

Cross-file relationships:
- Public macros and prototypes are in `messages.h`.
- Uses filesystem state and mount option definitions from `fs.h`/`super.h`, and stops discard through `discard.h`.
