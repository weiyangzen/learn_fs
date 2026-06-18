# File Research: sources/os/linux/linux/fs/xfs/xfs_mru_cache.c

## Purpose

`xfs_mru_cache.c` implements a time-bucketed most-recently-used cache for XFS clients. Elements are keyed by `unsigned long`, stored in a radix tree for lookup, and grouped into time lists for periodic expiration.

## Design

The cache uses:

- a radix tree for key-to-element lookup,
- an array of list heads representing discrete time groups,
- a reap list for expired elements,
- a spinlock protecting internal state,
- delayed work for timed reaping,
- a client-provided free callback.

Elements do not store individual expiration timestamps. Instead, the cache advances a time window and migrates old whole buckets to the reap list. This reduces per-element memory and enables grouped expiration.

## Main Functions

- `xfs_mru_cache_init`: creates the global MRU reaper workqueue.
- `xfs_mru_cache_uninit`: destroys the global workqueue.
- `xfs_mru_cache_create`: allocates and initializes a cache instance.
- `xfs_mru_cache_destroy`: flushes and frees a cache.
- `xfs_mru_cache_insert`: inserts an element into the radix tree and current MRU bucket.
- `xfs_mru_cache_remove`: removes an element without calling the free callback.
- `xfs_mru_cache_delete`: removes and frees an element.
- `xfs_mru_cache_lookup`: looks up an element, refreshes it into the current MRU bucket, and returns with the cache lock held.
- `xfs_mru_cache_done`: releases the lock after a successful lookup.

## Internal Helpers

- `_xfs_mru_cache_migrate`: advances time buckets and moves expired lists to the reap list.
- `_xfs_mru_cache_list_insert`: migrates buckets and inserts an element into the current bucket.
- `_xfs_mru_cache_clear_reap_list`: removes expired elements from radix tree and calls free callbacks outside the spinlock.
- `_xfs_mru_cache_reap`: delayed-work callback that migrates and frees expired elements, then reschedules itself if needed.
- `xfs_mru_cache_flush`: cancels pending work and expires all remaining elements.

## Locking Contract

`xfs_mru_cache_lookup` is unusual: on success it returns with the internal spinlock held so the caller can inspect or update the element cheaply. The caller must call `xfs_mru_cache_done`. On lookup miss, the function releases the lock before returning `NULL`.

## Error Handling

Creation validates non-null output pointer, nonzero lifetime, nonzero group count, nonzero computed group time, and non-null free callback. Insert preloads radix-tree memory and frees the element via the callback on failure.

## Notes

An extra list group is allocated to avoid reaping elements up to one group interval too early. The implementation uses `__GFP_NOFAIL` allocations for cache and list structures.
