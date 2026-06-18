<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/persistent_cache_helper.h -->
# sources/storage-engines/rocksdb/table/persistent_cache_helper.h

Purpose: Declares `PersistentCacheHelper`, a small static utility facade for table code to read and write RocksDB persistent cache entries.

Important APIs and types: The class exposes `InsertSerialized()`, `InsertUncompressed()`, `LookupSerialized()`, and `LookupUncompressed()`. Serialized operations include block trailers and are for compressed persistent caches. Uncompressed operations operate on `BlockContents` data without trailers and are for uncompressed persistent caches.

Control flow: Callers pass `PersistentCacheOptions` plus a `BlockHandle`; helper implementations construct cache keys consistently with block-based tables and route to the configured persistent cache.

State and persistence: The header owns no state. The API mutates the persistent cache supplied through options and returns `Status` for lookup operations.

Dependencies and integration points: Includes statistics support, table format types, and `persistent_cache_options.h`. It is consumed by lower-level block fetch/read logic that wants persistent cache behavior without duplicating key construction and stats recording.

Risks: The helper assumes the caller has validated cache availability and selected the correct compressed/uncompressed path. Because insertion returns `void`, cache write failures do not propagate to table reads.

Test signals: Compile coverage in block fetcher/table reader code, lookup status propagation, serialized/uncompressed cache mode assertions, and cache key consistency with block-based table keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/persistent_cache_helper.h -->
