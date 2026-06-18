# File Research: sources/os/linux/linux/fs/ntfs/debug.h

Declares NTFS logging macros and debug-only helpers.

Exports:
- `ntfs_debug()` maps to `__ntfs_debug()` in DEBUG builds and to a compile-time no-op wrapper otherwise.
- `ntfs_debug_dump_runlist()` is available only in DEBUG builds and becomes a no-op otherwise.
- `ntfs_warning()` wraps `__ntfs_warning()` with `__func__`.
- `ntfs_error()` wraps `__ntfs_error()` with `__func__`.
- `ntfs_handle_error()` is declared for error escalation.

Core mechanics:
- Non-DEBUG no-op macros still type-check format arguments through unreachable `no_printk()` branches.
- Logging helpers include the calling function automatically.

Notable risks:
- Whether an error marks the volume depends on callers passing a non-NULL superblock to `ntfs_error()`.
