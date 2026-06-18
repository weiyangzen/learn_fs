# File Research: sources/os/linux/linux/fs/cachefiles/cache.c

## Purpose
Manages high-level cache lifecycle: binding a cache root, validating the backing filesystem, registering with FS-Cache, computing space thresholds, checking available space, withdrawing objects/volumes, and syncing the backing filesystem on shutdown.

## Main Elements
- `cachefiles_add_cache()`: acquires an FS-Cache cache cookie, prepares security credentials, opens the configured cache root, rejects idmapped/read-only/unsupported filesystems, computes block/file thresholds, creates or pins `cache` and `graveyard` directories, and registers `cachefiles_cache_ops`.
- `cachefiles_has_space()`: runs `statfs`, accounts pending writes, checks file and block thresholds, records FS-Cache no-space counters, and toggles culling state.
- `cachefiles_withdraw_objects()`: removes active objects from the cache list and withdraws their FS-Cache cookies.
- `cachefiles_withdraw_fscache_volumes()` and `cachefiles_withdraw_volumes()`: coordinate FS-Cache volume withdrawal and CacheFiles volume cleanup.
- `cachefiles_sync_cache()`: syncs the backing superblock under CacheFiles credentials and marks the cache dead on serious I/O errors.
- `cachefiles_withdraw_cache()`: top-level cache unregister path.

## Dependencies And Integration
Uses VFS path lookup, `statfs`, mount and superblock operations, CacheFiles security overrides, CacheFiles directory helpers from `namei.c`, volume/object lists, and FS-Cache registration and withdrawal APIs.

## Risk Notes
Backing filesystem capability checks are central: CacheFiles needs lookup, mkdir, tmpfile, xattrs, statfs, sync, and page-sized-or-smaller blocks. Space threshold arithmetic is based on current `statfs` values, and errors such as `-EIO` transition the cache to a dead state. Withdrawal must coordinate object list removal with FS-Cache access counts.
