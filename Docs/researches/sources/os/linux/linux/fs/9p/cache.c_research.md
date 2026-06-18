# File Research: sources/os/linux/linux/fs/9p/cache.c

Implements the 9p client’s FS-Cache integration when `CONFIG_9P_FSCACHE` is enabled.

Key behavior:
- `v9fs_cache_session_get_cookie()` creates a per-session FS-Cache volume key from the mount source plus `cachetag` or `aname`.
- It rewrites `/` characters in the generated volume name to `;` so the key is usable by FS-Cache.
- Handles `fscache_acquire_volume()` errors, treating `-EBUSY` as a nonfatal duplicate-key condition with caching disabled for that session.
- `v9fs_cache_inode_get_cookie()` creates per-regular-file cookies keyed by the inode’s 9p `qid.path`, with coherency data from `qid.version`.
- Only regular files receive inode cookies.
- If a cookie is acquired, the mapping is marked with `mapping_set_release_always()` so FS-Cache release is reliably triggered.

Important interactions:
- Uses `struct v9fs_session_info::fscache` and `struct v9fs_inode::netfs`.
- Tied to 9p cache modes from `v9fs.h`, especially `CACHE_FSCACHE`.
- The cookie coherency model depends on server-provided `qid.version`, unless the mount ignores QID version elsewhere.
