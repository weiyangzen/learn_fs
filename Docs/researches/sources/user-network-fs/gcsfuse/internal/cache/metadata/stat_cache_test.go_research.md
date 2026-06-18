<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/metadata/stat_cache_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/cache/metadata/stat_cache_test.go

Purpose: validates the metadata stat cache bucket-view behavior for object entries, negative entries, folder entries, implicit directories, shared multi-bucket cache keys, expiration, and LRU eviction.

Important APIs/types/functions: `TestStatCache`, `testHelperCache`, `testMultiBucketCacheHelper`, `StatCacheTest`, `MultiBucketStatCacheTest`, and test cases around `Insert`, `InsertFolder`, `InsertImplicitDir`, `AddNegativeEntry`, `AddNegativeEntryForFolder`, `LookUp`, `LookUpFolder`, `EraseEntriesWithGivenPrefix`, and `NewStatCacheBucketView`.

Control flow: each suite creates an `lru.Cache` sized from `cfg.AverageSizeOfPositiveStatCacheEntry` and `cfg.AverageSizeOfNegativeStatCacheEntry`, wraps it as one or more bucket views, inserts entries with fixed expirations, and probes lookup results before, at, and after expiration. Multi-bucket tests use the same LRU backing cache with different bucket prefixes to prove same object names do not collide across bucket views.

State and persistence: all state is in-memory only. The tests deliberately mutate cache contents and LRU recency through lookup calls, so insertion order and access order are part of the asserted behavior. There is no disk persistence.

Dependencies and integration points: depends on `internal/cache/lru`, `internal/cache/metadata`, `internal/storage/gcs`, `cfg` cache sizing constants, `testify/suite`, and `assert`. These tests are direct unit coverage for metadata caching used by storage fast-stat layers and filesystem directory/type lookup paths.

Risks: many legacy cases exercise a helper wrapper instead of calling the production cache directly; the file comments call out that this weakens the safety net. Capacity assertions rely on approximate entry-size constants and could become brittle if cache-entry accounting changes. Expiration semantics are boundary-sensitive: entries are expected valid at exactly the expiration time and invalid after.

Test signals: strong coverage for generation/metageneration overwrite ordering, positive-negative replacement, folder negative entries, prefix erasure, implicit-directory compaction, implicit versus explicit precedence, and bucket-name isolation in a shared cache.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/metadata/stat_cache_test.go -->
