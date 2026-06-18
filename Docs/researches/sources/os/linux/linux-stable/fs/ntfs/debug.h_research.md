# File Research: sources/os/linux/linux-stable/fs/ntfs/debug.h

Purpose: Logging macro interface for NTFS code.

Key contents:
- In `DEBUG` builds, declares `debug_msgs`, `__ntfs_debug()`, and maps `ntfs_debug()` to include file, line, and function.
- In non-debug builds, `ntfs_debug()` and `ntfs_debug_dump_runlist()` compile to no-op constructs that still type-check format arguments.
- Declares `__ntfs_warning()` and `__ntfs_error()` with printf format attributes.
- Defines `ntfs_warning()` and `ntfs_error()` macros that inject `__func__`.
- Declares `ntfs_handle_error()`.

Role:
- Centralizes NTFS diagnostics and ensures errors can trigger filesystem error handling while warnings remain diagnostic.
