# File Research: sources/os/linux/linux/fs/9p/cache.h

Declares the 9p FS-Cache helper interface.

Key behavior:
- Under `CONFIG_9P_FSCACHE`, includes `<linux/fscache.h>` and declares:
  - `v9fs_cache_session_get_cookie()`
  - `v9fs_cache_inode_get_cookie()`
- Without FS-Cache support, provides a no-op inline `v9fs_cache_inode_get_cookie()`.

Important interactions:
- Allows the rest of 9p to call inode cache setup unconditionally while compiling out FS-Cache behavior when disabled.
- The session cookie acquisition helper is only available when FS-Cache is configured.
