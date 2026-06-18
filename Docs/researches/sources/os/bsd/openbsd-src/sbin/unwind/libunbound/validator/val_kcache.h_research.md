# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_kcache.h

## Purpose
Declares the validator key cache API.

## Main Type
`struct key_cache` wraps a `struct slabhash*` that stores `key_entry_key` / `key_entry_data` pairs.

## Public API
- `key_cache_create`: create cache from config.
- `key_cache_delete`: free cache.
- `key_cache_insert`: copy and insert/update a key entry.
- `key_cache_remove`: remove exact key entry by name/class.
- `key_cache_obtain`: find the closest unexpired key entry above a query name and copy it to a region.
- `key_cache_get_mem`: report memory usage.

## Integration
This header connects validator chain logic with the shared cache and depends on `util/storage/slabhash.h`. Concrete key-entry semantics are defined in `val_kentry.h`.

## Notable Constraints
Insertion may silently fail on memory pressure, as documented. Consumers must tolerate cache misses.
