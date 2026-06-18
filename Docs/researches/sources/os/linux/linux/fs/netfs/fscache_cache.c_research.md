# File Research: sources/os/linux/linux/fs/netfs/fscache_cache.c

## Role

FS-Cache cache-level registry and lifecycle management. It allocates cache records, looks up or names caches, transitions caches through preparing/active/withdrawn/error states, pins active caches during access, handles reference release, and exposes cache state through procfs when enabled.

## Global State

- `fscache_caches`: global list of cache records.
- `fscache_addremove_sem`: exported rwsem protecting cache list add/remove and cache registration state changes.
- `fscache_clearance_waiters`: exported waitqueue used by broader FS-Cache clearance logic.
- `fscache_cache_debug_id`: atomic counter assigning trace/debug IDs to caches.

## Cache Lookup and Acquisition

- `fscache_alloc_cache()` allocates a cache record, optionally duplicates a name, initializes the refcount/list node, and assigns a debug ID.
- `fscache_get_cache_maybe()` conditionally increments a nonzero refcount and traces acquisition.
- `fscache_lookup_cache()`:
  - first searches under read lock for an exact named or unnamed cache;
  - for unnamed lookups, can return the first named cache;
  - if not found, allocates a candidate and retries under write lock;
  - can convert an unnamed cache into a named cache when a backend cache registers with `is_cache=true`;
  - otherwise inserts the new candidate in the global list.
- `fscache_acquire_cache()` requires a name, looks up the cache, and atomically transitions it from `FSCACHE_CACHE_IS_NOT_PRESENT` to `FSCACHE_CACHE_IS_PREPARING`; if already in use it returns `-EBUSY`.

## Registration, Access, and Withdrawal

- `fscache_add_cache()` requires the preparing state, pins `n_accesses`, installs backend ops/private data, marks the cache active, and logs the cache addition.
- `fscache_begin_cache_access()` permits access only while the cache is live:
  - checks active state;
  - increments `n_accesses`;
  - uses an atomic barrier and rechecks liveness;
  - rolls back if the cache became inactive.
- `fscache_end_cache_access()` decrements `n_accesses`, traces the transition, and wakes waiters when it reaches zero.
- `fscache_io_error()` transitions an active cache to `FSCACHE_CACHE_GOT_IOERROR` and logs that the cache stopped due to I/O error.
- `fscache_withdraw_cache()` marks the cache withdrawn, drops the artificial active pin, traces the unpin, and waits until `n_accesses` reaches zero.

## Release

- `fscache_put_cache()` drops a cache reference, traces it, and on final reference removes the cache from the global list under write lock, frees the name, and frees the record.
- `fscache_relinquish_cache()` clears backend ops/private data, resets state to not-present, and releases the caller reference with a trace reason distinguishing preparation failure from normal relinquish.

## Procfs Reporting

When `CONFIG_PROC_FS` is enabled:

- `fscache_cache_states` maps cache states to single-character display codes.
- `fscache_caches_seq_show()` prints a header or one cache row containing debug ID, refcount, volume count, object count, access count, state character, and name.
- seq iteration holds `fscache_addremove_sem` for reading across traversal.
- `fscache_caches_seq_ops` exposes start/next/stop/show operations.

## Dependencies

Uses FS-Cache internal state helpers, tracepoints, Linux refcount/atomic/list/rwsem/waitqueue APIs, proc seq APIs, backend `fscache_cache_ops`, and exported synchronization primitives consumed by other FS-Cache code.

## Research Notes

The file separates cache object references from active access pins. References manage record lifetime, while `n_accesses` allows withdrawal to stop new users and wait for in-flight users. The unnamed-cache adoption path lets volumes discover a placeholder before a backend cache is fully named and registered.
