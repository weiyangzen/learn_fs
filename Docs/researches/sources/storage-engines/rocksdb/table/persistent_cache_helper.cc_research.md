<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/persistent_cache_helper.cc -->
# sources/storage-engines/rocksdb/table/persistent_cache_helper.cc

Purpose: Implements helper functions for looking up and inserting serialized or uncompressed blocks in RocksDB's persistent cache.

Important APIs and functions: Defines `PersistentCacheOptions::kEmpty` and implements `PersistentCacheHelper::InsertSerialized`, `InsertUncompressed`, `LookupSerialized`, and `LookupUncompressed`.

Control flow: Each operation derives a `CacheKey` from `BlockBasedTable::GetCacheKey(base_cache_key, handle)`. Serialized inserts assert a compressed persistent cache and store block bytes including trailer. Uncompressed inserts assert an uncompressed cache and store `BlockContents::data` without trailer. Serialized lookups fetch bytes into an owned buffer, record hit/miss ticks, and in debug verify expected size equals `handle.size() + kBlockTrailerSize`. Uncompressed lookups optionally return `NotFound` when no output `BlockContents` is provided, then populate `BlockContents` from the returned allocation on hit.

State and persistence: The helper mutates the configured persistent cache and statistics counters. It does not own cache lifetime; `PersistentCacheOptions` provides the shared cache pointer, base key, and stats pointer. Insert errors are explicitly ignored with `PermitUncheckedError()`.

Dependencies and integration points: Used by block fetching/table reading paths. Depends on `PersistentCache`, block handles, block contents, block-based cache key construction, and RocksDB statistics tick IDs `PERSISTENT_CACHE_HIT` and `PERSISTENT_CACHE_MISS`.

Risks: Correctness relies on callers choosing the serialized vs uncompressed helper matching the cache mode. Insert failures are non-fatal and invisible except through cache behavior. Debug-only size checks can hide production cache corruption until consumers parse the data. Uncompressed size assertions compare file compressed size to cache uncompressed size only loosely.

Test signals: Persistent cache hit/miss stats, compressed cache serialized round trip, uncompressed cache `BlockContents` round trip, missing cache entry behavior, null output for uncompressed lookup, and wrong-mode assertions in debug builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/persistent_cache_helper.cc -->
