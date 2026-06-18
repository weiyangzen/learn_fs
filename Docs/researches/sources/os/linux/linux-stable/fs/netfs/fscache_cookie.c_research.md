# File Research: sources/os/linux/linux-stable/fs/netfs/fscache_cookie.c

Implements FS-Cache data-object cookie lifecycle management for netfs users. It owns cookie allocation, key hashing, collision handling, use/unuse accounting, state transitions, invalidation, withdrawal, relinquishment, LRU expiry, and `/proc` cookie listing.

Key behavior:
- Maintains a hash table keyed by volume plus object key, with collision waiting when an older relinquished cookie is still dropping.
- Uses `n_active` for netfs use pins and `n_accesses` for active cache backend access pins.
- Cookie states include quiescent, looking up, creating, active, invalidating, failed, LRU discarding, withdrawing, relinquishing, and dropped.
- `__fscache_use_cookie()` starts lookup or marks local-write preparation; `__fscache_unuse_cookie()` updates aux/size and moves idle cached cookies to the LRU.
- Worker-driven state machine calls backend operations such as `lookup_cookie()`, `prepare_to_write()`, `invalidate_cookie()`, and `withdraw_cookie()`.
- LRU expiry sets `FSCACHE_COOKIE_DO_LRU_DISCARD` and withdraws backing storage if the cookie remains idle.
- Relinquish removes the cookie from the hash only after cached state has been withdrawn or immediately if never cached.
- Proc output exposes cookie id, volume id, refs, active/access counts, state, flags, key, and aux data.

Dependencies:
- Uses `fscache_volume.c` for volume references and access pins.
- Uses cache backend ops from `struct fscache_cache_ops`.
- Exports core FS-Cache cookie APIs to netfs/filesystem clients.
