# File Research: sources/os/linux/linux-stable/fs/ntfs/debug.c

Purpose: NTFS logging and debug-only runlist dump support.

Key responsibilities:
- `__ntfs_warning()` formats warning messages with optional superblock device context. In non-debug builds it uses ratelimited warnings.
- `__ntfs_error()` formats error messages with optional superblock device context. In non-debug builds it uses ratelimited errors and calls `ntfs_handle_error(sb)` when a superblock is present.
- Under `DEBUG`, defines global `debug_msgs`, implements `__ntfs_debug()`, and provides `ntfs_debug_dump_runlist()`.

Important behavior:
- Logging wrappers include the caller function name via macros in `debug.h`.
- `ntfs_debug_dump_runlist()` prints VCN, LCN or symbolic negative LCN state, and run length until the terminating zero-length element.
- Debug output is controlled at runtime by `debug_msgs` when compiled with `DEBUG`.

Dependencies:
- Includes `debug.h`, which includes runlist declarations.
- `ntfs_handle_error()` is declared in `debug.h` and implemented elsewhere.

Risk notes:
- Error logging has side effects through `ntfs_handle_error(sb)`, so `ntfs_error()` is not just diagnostic.
