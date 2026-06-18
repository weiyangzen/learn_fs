# File Research: sources/os/linux/linux/fs/netfs/fscache_cookie.c

Implements FS-Cache data-object cookie lifecycle management for the netfs cache API.

Key responsibilities:
- Allocates/free cookies from `fscache_cookie_jar`.
- Maintains global cookie hash table keyed by volume plus index key.
- Tracks cookies in `/proc` list and LRU list.
- Drives the cookie state machine: `QUIESCENT`, `LOOKING_UP`, `CREATING`, `ACTIVE`, `INVALIDATING`, `FAILED`, `LRU_DISCARDING`, `WITHDRAWING`, `RELINQUISHING`, `DROPPED`.
- Pins cache access with `n_accesses` and netfs use with `n_active`.
- Handles lookup, prepare-to-write, invalidation, withdrawal, relinquishment, LRU discard, and collision waiting.

Important exported APIs:
- `__fscache_acquire_cookie()`: creates and hashes a cookie.
- `__fscache_use_cookie()`: starts using a cookie and may begin lookup.
- `__fscache_unuse_cookie()`: stops using a cookie and places it on LRU if cacheable.
- `__fscache_relinquish_cookie()`: releases a cookie permanently.
- `__fscache_invalidate()`: invalidates object data and updates auxiliary coherency data.
- `fscache_begin_cookie_access()` / `fscache_end_cookie_access()`: guard I/O access against cache withdrawal.
- `fscache_withdraw_cookie()`, `fscache_get_cookie()`, `fscache_put_cookie()`.

Concurrency model:
- Cookie state protected by `cookie->lock`, published with release/acquire semantics.
- Hash buckets use `hlist_bl_lock`.
- Proc list uses `fscache_cookies_lock`.
- LRU list uses `fscache_cookie_lru_lock` plus timer/workqueue.
- Waiters use `wait_var_event()` on `cookie->state`.

Notable behavior:
- Duplicate active cookies are rejected; collisions with relinquished cookies wait until the old cookie reaches `DROPPED`.
- LRU discard is postponed if `n_active` or `n_accesses` indicates active use.
- Invalidation can be queued during lookup/creation or performed immediately when active.
- Failure clears `FSCACHE_COOKIE_IS_CACHING` and moves to `FAILED`.
- `/proc/fs/netfs/cookies` exposes debug id, volume id, refs, active/access counts, state, flags, key, and auxiliary data.

Dependencies:
- Uses cache backend operations through `cookie->volume->cache->ops`.
- Relies on `fscache_volume.c` for volume lifetime and cache access.
- Statistics are updated through `fscache_stats.c`.
