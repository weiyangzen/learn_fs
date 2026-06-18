# File Research: sources/os/linux/linux-stable/fs/netfs/fscache_cache.c

## Purpose

`fscache_cache.c` implements FS-Cache cache-level object management. It tracks registered cache backends, cache acquisition/relinquish, live access pinning, I/O error state, withdrawal, and optional procfs listing.

This is the global cache registry layer beneath netfs/FS-Cache cookies and volumes.

## Main Globals

- `fscache_caches`: global list of cache records.
- `fscache_addremove_sem`: rwsem protecting cache add/remove/lookup.
- `fscache_clearance_waiters`: waitqueue exported for cache clearance users.
- `fscache_cache_debug_id`: atomic ID source for trace/debug identifiers.

Exported globals:

- `fscache_addremove_sem`
- `fscache_clearance_waiters`

## Cache Allocation And Lookup

`fscache_alloc_cache(const char *name)`:

- Allocates and zeroes `struct fscache_cache`.
- Optionally duplicates the cache name.
- Initializes refcount to 1.
- Initializes list linkage.
- Assigns debug ID.

`fscache_lookup_cache(const char *name, bool is_cache)`:

- First searches under read lock.
- Matches named cache by exact name.
- Matches unnamed cache if both requested and existing are unnamed.
- If no name is requested, can fall back to the first named cache.
- If not found, allocates a candidate and retries under write lock.
- If an unnamed cache exists and caller is acquiring a real cache, it can assign the candidate name to that unnamed cache.
- Adds a new cache to `fscache_caches` if still absent.
- Uses refcount-not-zero acquisition to avoid resurrecting freed caches.

The unnamed-cache behavior lets consumers initially refer to a default cache and later bind it to a named backend.

## Cache Acquisition And Release

`fscache_acquire_cache(const char *name)`:

- Requires a name.
- Looks up or creates a cache record.
- Transitions state from `FSCACHE_CACHE_IS_NOT_PRESENT` to `FSCACHE_CACHE_IS_PREPARING`.
- Returns `-EBUSY` if a cache tag is already in use.

`fscache_put_cache(struct fscache_cache *cache, enum fscache_cache_trace where)`:

- Drops a reference.
- Removes the cache from the global list and frees name/object when refcount reaches zero.
- Emits trace events.

`fscache_relinquish_cache(struct fscache_cache *cache)`:

- Clears ops and private data.
- Resets state to not-present.
- Drops the caller reference with trace reason depending on whether preparation failed or active cache was relinquished.

## Adding And Withdrawing Cache Backends

`fscache_add_cache(struct fscache_cache *cache, const struct fscache_cache_ops *ops, void *cache_priv)`:

- Requires state `FSCACHE_CACHE_IS_PREPARING`.
- Pins `n_accesses` by incrementing it, preventing withdrawal waitups from reaching zero during active service.
- Stores backend ops and private data under write lock.
- Sets state active.
- Logs cache addition.

`fscache_withdraw_cache(struct fscache_cache *cache)`:

- Sets state withdrawn.
- Drops the artificial service pin on `n_accesses`.
- Waits until active accesses drain to zero.
- Logs withdrawal with object count.

## Access Pinning

`fscache_begin_cache_access(struct fscache_cache *cache, enum fscache_access_trace why)`:

- Checks cache is live.
- Increments `n_accesses`.
- Uses memory barrier after atomic increment and rechecks liveness.
- If cache went non-live, immediately ends access and returns false.
- Otherwise returns true.

`fscache_end_cache_access(struct fscache_cache *cache, enum fscache_access_trace why)`:

- Uses memory barrier before decrement.
- Decrements `n_accesses`.
- Wakes waiters when it reaches zero.

This prevents cache backends from being withdrawn while operations are actively using them.

## I/O Error Handling

`fscache_io_error(struct fscache_cache *cache)`:

- Transitions active cache to `FSCACHE_CACHE_GOT_IOERROR`.
- Logs that the cache stopped due to I/O error.
- Exported for backend use.

## Procfs Listing

When `CONFIG_PROC_FS` is enabled, the file defines `fscache_caches_seq_ops` for `/proc/fs/fscache/caches`.

The seq output includes:

- Cache debug ID.
- Refcount.
- Volume count.
- Object count.
- Active access count.
- Cache state character.
- Cache name or `-`.

Iteration holds `fscache_addremove_sem` read lock across seq traversal.

## Synchronization

- Cache registry mutations use `fscache_addremove_sem`.
- Per-cache lifetime uses `refcount_t`.
- Active use uses `atomic_t n_accesses`.
- Cache state transitions use helper functions/macros from internal FS-Cache code.
- Memory barriers around access counters enforce live-state visibility.

## Exports

Exports:

- `fscache_acquire_cache`
- `fscache_put_cache`
- `fscache_relinquish_cache`
- `fscache_add_cache`
- `fscache_io_error`
- `fscache_withdraw_cache`

## Key Takeaways

This file is the FS-Cache backend registry and lifetime manager. It separates cache record references from active access pins, supports named/default cache lookup, provides a prepare-active-withdraw state model, and exposes cache state for diagnostics through procfs.
