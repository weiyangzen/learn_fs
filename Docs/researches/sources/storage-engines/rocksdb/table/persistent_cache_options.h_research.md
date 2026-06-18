<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/persistent_cache_options.h -->
# sources/storage-engines/rocksdb/table/persistent_cache_options.h

Purpose: Defines the lightweight context object passed through table/block read paths to enable persistent cache use.

Important APIs and types: `PersistentCacheOptions` contains a `std::shared_ptr<PersistentCache> persistent_cache`, an `OffsetableCacheKey base_cache_key`, and a `Statistics* statistics`. It provides a default constructor, a field-initializing constructor, and static `kEmpty`.

Control flow: Table readers construct non-empty options when a persistent cache should be consulted. Helpers and block fetchers pass `kEmpty` or a configured instance depending on whether cache participation is desired.

State and persistence: The struct does not persist data itself but points to the persistent cache backend and provides the base key namespace used to persist block entries. `statistics` may be null, in which case tick recording is effectively optional through statistics helpers.

Dependencies and integration points: Depends on RocksDB persistent cache API, cache key utilities, and statistics definitions. It is used by `PersistentCacheHelper`, block fetching, and meta block reading.

Risks: A default-constructed instance has no cache; helper calls generally assert a non-null cache. Incorrect base cache keys can cross-contaminate cached blocks between files. The shared pointer lifetime makes cache ownership explicit but does not guarantee the underlying cache content is valid for a specific file version.

Test signals: Empty option pass-through, configured option propagation from table reader to block fetcher, cache key namespacing by file, and stats pointer behavior when null or non-null.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/persistent_cache_options.h -->
