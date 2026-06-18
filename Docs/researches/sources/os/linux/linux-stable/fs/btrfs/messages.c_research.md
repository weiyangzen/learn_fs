# File Research: sources/os/linux/linux-stable/fs/btrfs/messages.c

## Summary
Implements Btrfs logging, error decoding, filesystem error handling, fatal panic handling, and 32-bit logical-address limit warnings.

## Main Responsibilities
- Converts filesystem state bits into compact printable state suffixes.
- Decodes selected negative errno values into human-readable messages.
- Handles filesystem errors by recording the error and forcing the filesystem read-only after mount.
- Provides rate-limited Btrfs printk formatting by log level.
- Emits one-time warnings/errors for 32-bit page-cache address limits.
- Implements fatal panic/BUG policy depending on mount options.

## Key APIs
- `btrfs_decode_error()`.
- `__btrfs_handle_fs_error()`.
- `_btrfs_printk()`.
- `btrfs_warn_32bit_limit()`, `btrfs_err_32bit_limit()` on 32-bit builds.
- `__btrfs_panic()`.

## Important Behavior
`__btrfs_handle_fs_error()` ignores `-EROFS` when the superblock is already read-only, prints a critical message with device, function, line, errno, decoded error, and optional format string, records `fs_error`, and forces the filesystem read-only once the superblock is born.

Before forcing read-only, it stops discard. It intentionally does not cancel device replace to avoid deadlock risk; replacement may continue until completion.

`_btrfs_printk()` uses one ratelimit state per log level so lower-priority floods do not suppress higher-priority messages. It includes filesystem state characters when an `fs_info` is available.

`__btrfs_panic()` panics only when the filesystem has `PANIC_ON_FATAL_ERROR`; otherwise it logs a critical message and relies on the caller macro to `BUG()`.

## State and Synchronization
Filesystem state is read with `READ_ONCE()`. Superblock label/state access in callers may require their own locks. Printing is conditional on `CONFIG_PRINTK`.

## Risks
The error path is intentionally one-way for mounted writable filesystems: after serious errors, the filesystem is forced read-only. Callers must choose error codes carefully because subsequent generic failures caused by prior FS error should use `-EROFS`.
