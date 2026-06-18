# File Research: sources/os/linux/linux-stable/fs/ocfs2/super.h

Declares OCFS2 superblock-level error and signal helper APIs.

Key contents:
- Declares `__ocfs2_error()` and wraps it with `ocfs2_error(sb, fmt, ...)`, passing `__PRETTY_FUNCTION__` for diagnostic context.
- Declares `__ocfs2_abort()` and wraps it with `ocfs2_abort(sb, fmt, ...)`, also recording the caller function.
- Declares `ocfs2_block_signals()` and `ocfs2_unblock_signals()` for temporarily blocking all signals and restoring the previous signal mask.

Integration points:
- Metadata validation, allocator, journal, mount, and inode paths call `ocfs2_error()` for on-disk corruption.
- Critical journal/filesystem failures call `ocfs2_abort()` when continuing is unsafe.
- Long critical sections that cannot tolerate signals use the signal helpers.

Risk areas:
- These macros are part of OCFS2’s corruption policy surface; callers should use `ocfs2_error()` only for genuine filesystem inconsistency because it may remount read-only or panic depending on mount options.
- `ocfs2_abort()` is intentionally drastic for clustered mounts.
