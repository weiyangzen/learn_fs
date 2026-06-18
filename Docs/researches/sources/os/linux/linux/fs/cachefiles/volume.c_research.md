# File Research: sources/os/linux/linux/fs/cachefiles/volume.c

## Purpose
Creates, validates, pins, withdraws, and frees CacheFiles volume directories and their 256 fanout subdirectories.

## Main Elements
- `cachefiles_acquire_volume()`: allocates a volume object, creates or opens the volume directory from the FS-Cache volume key, sets or validates volume xattrs, creates and pins `@00` through `@ff` fanout directories, and links the volume into the cache list.
- `__cachefiles_free_volume()`: releases all fanout directories and the volume directory and clears `vcookie->cache_priv`.
- `cachefiles_free_volume()`: removes the volume from the cache list and frees it.
- `cachefiles_withdraw_volume()`: writes volume xattrs and frees the volume during cache withdrawal.

## Dependencies And Integration
Uses directory helpers from `namei.c`, xattr coherency from `xattr.c`, FS-Cache volume access counters, and CacheFiles cache object-list locking.

## Risk Notes
Existing volume directories with stale xattrs are buried and retried. Partial fanout creation failure must release all already pinned directories. The volume is pinned by an FS-Cache access count to suppress premature wakeups.
