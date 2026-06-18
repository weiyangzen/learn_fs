# File Research: sources/local-fs/ntfs-3g/libntfs-3g/cache.c

## Scope

Implements generic fixed-size LRU caches used by NTFS-3G for inode, directory lookup, security ID, and permissions-related cached records.

## API And Behavior

- Cache entries are `CACHED_GENERIC` records with mandatory list fields, fixed payload storage, and optional variable-size allocation.
- Hash support is optional. `inserthashindex()` and `drophashindex()` maintain separate hash-entry chains; bad hash values or inconsistent chains disable hashing and fall back to sequential LRU scans.
- `ntfs_fetch_cache()` searches by hash when available or by LRU scan otherwise, increments read/hit counters, and promotes found entries to the most-recent position.
- `ntfs_enter_cache()` finds or creates an entry, reuses the oldest entry when full, copies fixed and variable payload data, invokes per-entry cleanup on eviction, and inserts a hash index if enabled.
- `ntfs_invalidate_cache()` removes all matching entries, using hash lookup unless `CACHE_NOHASH` is requested, then relinks entries onto the free list and optionally calls the cleanup hook.
- `ntfs_remove_cache()` removes a known entry directly.
- `ntfs_create_cache()` allocates one contiguous block containing the header, entries, optional hash entries, and optional hash buckets.
- `ntfs_create_lru_caches()` initializes volume-level caches according to compile-time cache size macros.
- `ntfs_free_lru_caches()` releases all volume-level caches and any variable data still attached to entries.

## State And Dependencies

The cache layer stores no NTFS semantics itself; behavior is supplied through compare, free, and hash callbacks. Volume cache fields include inode, named-data, lookup, security-ID, and legacy-permissions caches depending on build-time macros.

## Risks And Invariants

The design intentionally does not surface allocation/cache errors to callers; memory pressure simply makes entries uncached. Hashing can be disabled at runtime after internal consistency problems, preserving correctness through slower sequential scans. The implementation assumes at least enough entries for LRU reuse semantics and that callers do not free returned cache entries directly.
