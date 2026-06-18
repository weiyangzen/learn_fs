# File Research: sources/os/linux/linux/fs/ntfs/debug.c

Implements NTFS logging helpers and optional debug-only runlist dumping.

Key entry points:
- `__ntfs_warning()` emits warning messages with optional superblock device context.
- `__ntfs_error()` emits error messages and calls `ntfs_handle_error()` when a superblock is supplied.
- Under `DEBUG`, `__ntfs_debug()` emits debug messages when `debug_msgs` is enabled.
- Under `DEBUG`, `ntfs_debug_dump_runlist()` prints a runlist with readable labels for negative sentinel LCNs.

Core mechanics:
- Uses `struct va_format` to pass variadic messages to kernel `pr_warn`, `pr_err`, or `pr_debug`.
- Non-DEBUG warning/error messages are rate-limited; DEBUG builds are not rate-limited.
- Error logging with an `sb` triggers filesystem error handling.
- Runlist dumping iterates until a zero-length terminator and labels `LCN_DELALLOC`, `LCN_HOLE`, `LCN_RL_NOT_MAPPED`, `LCN_ENOENT`, or unknown negative LCNs.

Important invariants:
- `ntfs_debug_dump_runlist()` assumes caller-side synchronization for the runlist.
- `debug_msgs` gates DEBUG logging globally.

Notable risks:
- Calls to `ntfs_error()` with `sb == NULL` log but do not trigger `ntfs_handle_error()`.
