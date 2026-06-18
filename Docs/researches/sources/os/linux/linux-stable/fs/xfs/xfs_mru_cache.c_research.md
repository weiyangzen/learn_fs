# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_mru_cache.c

## Purpose
Implements a generic XFS most-recently-used cache with radix-tree lookup, grouped time-bucket expiry, delayed-work reaping, and client-provided element freeing.

## Main APIs
- `xfs_mru_cache_init` and `xfs_mru_cache_uninit` create/destroy the global MRU reaper workqueue.
- `xfs_mru_cache_create` allocates a cache with a lifetime, group count, private data pointer, and free callback.
- `xfs_mru_cache_destroy` flushes and frees a cache.
- `xfs_mru_cache_insert` inserts a caller-provided element under a key.
- `xfs_mru_cache_remove` removes an element without freeing it.
- `xfs_mru_cache_delete` removes and frees an element.
- `xfs_mru_cache_lookup` returns an element and moves it to the current MRU bucket while leaving the cache spinlock held.
- `xfs_mru_cache_done` releases the lookup-held spinlock.

## Key Behavior
Elements live in both a radix tree and a time-bucket list. The bucket array represents coarse time intervals; touching an item moves it to the current MRU bucket. Reaping migrates expired LRU buckets to a reap list and frees them outside the spinlock via the client callback.

## Lifetime Model
The implementation adds an extra bucket so elements are not reaped early. Depending on timer granularity, an inactive element can survive up to approximately one group interval beyond the requested lifetime. Delayed work schedules the next reap at the earliest needed time.

## Locking and Failure Handling
Internal state is protected by a spinlock. Lookup returns with the lock held only on success, requiring `xfs_mru_cache_done`. Insert preloads the radix tree with `GFP_KERNEL` before locking and frees the element through the callback on insert failure.
