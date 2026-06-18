# sources/storage-engines/rocksdb/util/compression_context_cache.h

Purpose: declares the process singleton used to cache compression/uncompression contexts, currently only ZSTD decompression contexts, on a per-core basis.

Important APIs and types: `CompressionContextCache::Instance()` returns the singleton, `InitSingleton()` forces construction, `GetCachedZSTDUncompressData()` borrows a cached or one-shot ZSTD context, and `ReturnCachedZSTDUncompressData(int64_t idx)` returns a previously borrowed cached context. The private `Rep` hides the `CoreLocalArray` implementation from users.

Control flow and state: users do not manage native codec pointers directly; they receive and return `ZSTDUncompressCachedData` through higher-level wrappers. The cache uses an index-based return protocol because the borrowing thread may not still be on the same core when it releases the context.

Dependencies and integration points: forward-declares `ZSTDUncompressCachedData` and includes only namespace definitions in the header, keeping codec and core-local details in the `.cc`. `UncompressionContext` in `compression.h` is the key integration point.

Risks: the public return method trusts the provided index and asserts on invalid values in the implementation. Because the cache is a singleton, teardown ordering can matter if other static objects try to return contexts after destruction; normal use scopes contexts inside operations.

Test signals: tested indirectly through ZSTD decompression and environment initialization; no standalone unit test validates singleton lifecycle.
