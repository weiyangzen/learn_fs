# sources/storage-engines/rocksdb/util/compression_context_cache.cc

Purpose: implements a singleton per-core cache of reusable ZSTD decompression contexts to reduce random-read latency and allocation/initialization overhead.

Important APIs and types: `compression_cache::ZSTDCachedData` contains one `ZSTDUncompressCachedData` and an atomic sentinel pointer. `CompressionContextCache::Rep` owns a `CoreLocalArray<ZSTDCachedData>` and exposes indexed borrow/return methods. Public methods forward through `rep_`: `GetCachedZSTDUncompressData()` and `ReturnCachedZSTDUncompressData()`.

Control flow: `Rep::GetZSTDUncompressData()` asks `CoreLocalArray` for the current core's element and index. `ZSTDCachedData::GetUncompressData()` tries to atomically swap the sentinel from the cached-data address to `nullptr`; success means the caller borrowed the per-core context and receives the cache index, while failure means another thread is using it and a one-time owned context is created instead. `ReturnZSTDUncompressData()` looks up the original core index and swaps the sentinel back to the cached-data address.

State and persistence: all state is process-local and non-persistent. The singleton is function-local static storage. Cached native contexts can live for process lifetime; one-shot contexts are freed by `ZSTDUncompressCachedData` destructors. `CompressionContextCache::InitSingleton()` eagerly constructs the singleton for environments that want initialization before worker use.

Dependencies and integration points: depends on `util/compression.h` for `ZSTDUncompressCachedData` and `util/core_local.h` for core sharding. Environment startup calls `CompressionContextCache::InitSingleton()` in POSIX and Windows default environments. `UncompressionContext` in `compression.h` is the main client and returns cached entries during destruction.

Risks: correctness depends on callers returning only borrowed entries and exactly once; `ReturnUncompressData()` asserts if the sentinel was not acquired. The cached core index can become stale if a thread migrates, but returning to the original index is intended because the borrowed object records that index. The padding expression is designed to make the structure cache-line sized, but changes to member sizes or `CACHE_LINE_SIZE` can affect compile-time layout.

Test signals: behavior is indirectly tested by ZSTD decompression paths in DB compression tests and WAL/table read tests. There is no direct stress test in this file for concurrent borrow fallback or assert paths.
