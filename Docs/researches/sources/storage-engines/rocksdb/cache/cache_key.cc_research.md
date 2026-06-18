# sources/storage-engines/rocksdb/cache/cache_key.cc

## Purpose
This file implements RocksDB's standardized 16-byte cache key generation, including cache-lifetime unique keys, process-lifetime unique keys, and file-offset-derived block cache keys based on SST internal unique IDs.

## Important APIs, types, and functions
`CacheKey::CreateUniqueForCacheLifetime(Cache*)` returns `(0, cache->NewId()+1)` and asserts the id does not enter the high-bit range reserved for process-lifetime keys. `CacheKey::CreateUniqueForProcessLifetime()` uses a static atomic counter starting at `UINT64_MAX`, counts down with relaxed ordering, and asserts the high bit is set. `OffsetableCacheKey(const std::string&, const std::string&, uint64_t)` calls `GetSstInternalUniqueId(..., force=true)` and delegates to `FromInternalUniqueId()`.

`OffsetableCacheKey::FromInternalUniqueId(UniqueIdPtr)` transforms two 64-bit internal ID words into a base cache key using `DownwardInvolution(session_lower)`, `ReverseBits(file_num_etc)`, and `ReverseBits(session_lower)`, preserving empty input as empty and swapping words if needed to ensure the first word is non-zero for non-empty keys. `ToInternalUniqueId()` reverses that transformation, with the same swap convention.

## Control flow, state, and persistence
The only mutable state is the process-lifetime atomic counter. File-derived keys are deterministic from persistent SST identity data (`db_id`, `db_session_id`, and file number), which lets cache keys remain stable across DB reopen, backup/restore, import/export, and persistent cache lookup. `WithOffset()` in the header later combines the base key with offsets by XORing the second word.

## Dependencies and integration points
The implementation depends on `rocksdb/advanced_cache.h`, SST unique ID helpers from `table/unique_id_impl.h`, hashing/math utilities such as `DownwardInvolution()` and `ReverseBits()`, and cache `NewId()`. It is used by block-based table readers, reservation dummy entries, process-shared cache metadata, and the cache-key stress simulation in `cache_bench_tool.cc`.

## Risks and test signals
The correctness argument is mathematical and relies on assumptions about SST unique ID structure, non-empty lower words, and structured values fitting into 128 bits. Endianness is intentionally not portable for persisted cache entries across platforms. Cache-lifetime keys assume `Cache::NewId()` counts from low values and never reaches the process-lifetime high-bit range. Test with cache-key encoder/decoder tests, `StressCacheKey`, collision simulations, persistent cache reopen scenarios, and assertions around empty/non-empty transformations.
