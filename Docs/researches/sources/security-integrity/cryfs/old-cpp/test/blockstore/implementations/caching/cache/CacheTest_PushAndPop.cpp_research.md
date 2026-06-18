# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/CacheTest_PushAndPop.cpp

Purpose: functional tests for cache insertion, lookup/removal, capacity eviction, ordering, and age timeout behavior.

Important APIs/types/functions: `CacheTest_PushAndPop`, fixture helpers `push` and `pop`, `MAX_ENTRIES`, `Cache::MAX_LIFETIME_SEC`, and `Cache::PURGE_LIFETIME_SEC`.

Control flow: tests empty, non-empty, and full cache misses; ordered and non-ordered push/pop sequences; eviction when exceeding capacity; and timeout eviction using sleeps around two inserted entries.

State and persistence behavior: all cache entries are in-memory. Pop removes entries; pushing beyond capacity evicts oldest entries; background/age cleanup affects timeout test.

Dependencies and integration points: uses `testutils/CacheTest.h`, `Cache`, minimal key/value types, Boost optional helpers, and Boost thread sleep.

Risks and test signals: good coverage of FIFO-like eviction and keyed pop. Timeout test depends on wall-clock timing and can be slow or flaky under heavy load.
