<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_pcache.c -->
# sources/storage-engines/sqlite/src/test_pcache.c

## Purpose
`test_pcache.c` is a deliberately simple application-defined pager-cache implementation used by SQLite tests. It replaces the default page cache to exercise pager behavior under cache pressure, random page discard, failed initialization, and aggressive stress paths.

## Important APIs, Types, And Functions
It implements `sqlite3_pcache_methods2` with `testpcacheInit()`, `testpcacheShutdown()`, `testpcacheCreate()`, `testpcacheFetch()`, `testpcacheUnpin()`, `testpcacheRekey()`, `testpcacheTruncate()`, and `testpcacheDestroy()`. `testpcacheGlobalType` stores installation-wide knobs: dummy allocation, instance count, discard chance, PRNG seed, and high-stress mode. `testpcache` owns a fixed array of page slots with keys and pin state.

## Control Flow
`installTestPCache()` saves or restores the default cache methods using `sqlite3_config()`. Initialization allocates a dummy block so tests can observe initialization failure and shutdown cleanup. Each cache instance allocates one block containing the instance and all page buffers. Fetch first returns an existing page, then optionally allocates a free slot, withholds reserve slots unless `createFlag==2`, may force failure in high-stress mode, and finally recycles a random unpinned page for purgeable caches. Unpin may discard based on the explicit discard flag or randomized discard probability.

## State And Persistence Behavior
All state is process-local and non-persistent. Page content is in heap memory. The fixed page array is a hard limit; `nFree` and `nPinned` track capacity and invariants. Randomness is deterministic from `prngSeed`, making stress behavior reproducible.

## Dependencies And Integration Points
The implementation plugs into SQLite through `SQLITE_CONFIG_PCACHE2` and is installed by test code before SQLite initialization. It assumes single-threaded use: the global state has no mutex protection.

## Risks And Test Signals
Risks include intentional lack of thread safety, fixed capacity differing with `SQLITE_TEMP_STORE`, reliance on asserts for invariants, and a suspicious alignment assignment in `testpcacheCreate()` where `szExtra` is rounded from `szPage` instead of its own value. Test signals include pager tests passing with random discard rates, high-stress mode invoking pager stress paths, no leaked instances on shutdown, correct rekey/truncate behavior, and deterministic failure reproduction from the same seed.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_pcache.c -->
