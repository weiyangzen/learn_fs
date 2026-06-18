# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_lru.h

## Purpose
`mdcache_lru.h` exposes the MDCACHE LRU/cache-lifetime API used by helper, hash, export, and handle code. It documents the LRU design, declares global LRU state and the cache-entry pool, and defines reference flags and queue sizing constants.

## Important APIs, Types, and Functions
- `struct lru_state` stores entry/chunk watermarks, current counts, per-lane work, release size, and prior run time.
- `LRU_ACTIVE_REF`, `LRU_PROMOTE`, `LRU_FLAG_SENTINEL`, and `LRU_TEMP_REF` describe reference intent.
- `LRU_SENTINEL_REFCOUNT` defines the base reachable reference count, and `LRU_N_Q_LANES` sets the prime number of queue lanes.
- Public entry APIs include `mdcache_lru_pkginit()`, `mdcache_lru_pkgshutdown()`, `mdcache_lru_get()`, `mdcache_lru_insert_active()`, `mdcache_lru_ref()`, `mdcache_lru_unref()`, cleanup push helpers, and `mdcache_lru_release_entries()`.
- Public chunk and dirmap APIs include chunk ref/unref/get/bump and `mdc_lru_map_dirent()`, `mdc_lru_unmap_dirent()`, `dirmap_lru_init()`, and `dirmap_lru_stop()`.

## Control Flow
The header establishes the required calling contract: newly allocated entries from `mdcache_lru_get()` must later be inserted, references must be released through `mdcache_lru_unref()`, and callers must not touch an entry after unref because it may free or recycle the object. Chunk APIs similarly require callers to respect content-lock expectations described in the implementation.

## State and Persistence Behavior
The exposed state is volatile process memory. `lru_state` is global and records resource pressure thresholds and counters; `mdcache_entry_pool` owns cache-entry allocations. No persistent data is written by this interface.

## Dependencies and Integration Points
The header depends on `mdcache_int.h`, logging, and FSAL types. It is the shared contract between `mdcache_helpers.c`, `mdcache_lru.c`, hash cleanup, and other MDCACHE handle/export code that needs object lifetime control.

## Risks and Edge Cases
The largest risk is misuse of reference flags: omitting `LRU_ACTIVE_REF`, incorrectly releasing the sentinel, or accessing entries after unref can cause leaks or use-after-free. The header declares `mdcache_lru_kill()` and `mdcache_lru_kill_for_shutdown()` even though their definitions are outside this file subset or absent in this implementation view, so consumers must verify linkage.

## Test Signals
Compilation/link tests should catch missing API definitions. Runtime tests should assert balanced refs for lookup/readdir/open paths, correct high-water release behavior, and safe chunk lifecycle under directory cache churn.
