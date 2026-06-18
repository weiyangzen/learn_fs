# File Research: sources/os/linux/linux-stable/fs/9p/cache.h
- Purpose: Declares 9P FS-Cache helpers and disabled-cache fallback behavior.
- Main exports: `v9fs_cache_session_get_cookie` and `v9fs_cache_inode_get_cookie`.
- Conditional behavior: With `CONFIG_9P_FSCACHE`, real helpers are used. Without it, inode cookie acquisition is an inline no-op.
- Integration: Included by session, inode, file, and address-space code that needs cache-aware behavior.
- Research notes: The header hides most compile-time differences from the rest of the 9P code.
