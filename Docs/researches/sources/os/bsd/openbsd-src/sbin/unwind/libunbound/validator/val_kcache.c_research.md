# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_kcache.c

## Purpose
Implements the validator key cache, a shared slabhash-backed cache of validated key entries and negative/insecure key states.

## Main Responsibilities
- Creates and destroys `struct key_cache`.
- Inserts copied `key_entry_key` objects into the slabhash.
- Looks up exact key entries under lock.
- Performs closest-enclosing key lookup by walking up labels from the queried name to root.
- Checks TTL before returning a region-allocated copy.
- Removes exact entries from the cache.
- Reports memory use.

## Key Functions
- `key_cache_create`: uses `cfg->key_cache_slabs` and `cfg->key_cache_size` to create the slabhash with key-entry callbacks.
- `key_cache_insert`: deep-copies a key entry, hashes it, and inserts it.
- `key_cache_search`: exact lookup helper returning a locked cache entry.
- `key_cache_obtain`: repeatedly searches the queried name and parent names until it finds an unexpired key entry or reaches root.
- `key_cache_remove`: exact remove by name/class.
- `key_cache_get_mem`: returns wrapper plus slabhash memory.

## Dependencies and Integration
Uses `val_kentry` for key-entry hashing/copy/delete callbacks, `slabhash` for concurrent cache storage, `dname_remove_label` for parent traversal, and Unbound configuration/logging.

## Notable Constraints
Expired entries are ignored by `key_cache_obtain` but not removed there. Returned entries are copies allocated in the caller's regional allocator, while the original cache entry lock is released before return.
