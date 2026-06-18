# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/CacheTest_RaceCondition.cpp

Purpose: regression tests for a cache race where `pop()` could return before an evicted entry's destructor finished writing back data.

Important APIs/types/functions: `ObjectWithLongDestructor`, `CacheTest_RaceCondition`, `ConditionBarrier`, `causeCacheOverflowInOtherThread`, `EXPECT_POP_BLOCKS_UNTIL_DESTRUCTOR_FINISHED`, and `EXPECT_POP_DOESNT_BLOCK_UNTIL_DESTRUCTOR_FINISHED`.

Control flow: pushes an object whose destructor signals start and sleeps. Tests trigger age-based or capacity-based eviction, wait until destruction starts, then call `pop` for either the same key or another key and assert blocking behavior.

State and persistence behavior: cache entries are in-memory, but the destructor models delayed persistence/writeback. Atomic `destructorFinished` records completion.

Dependencies and integration points: uses `Cache`, `std::async`, `std::atomic`, `ConditionBarrier`, and move-only `unique_ptr` values.

Risks and test signals: strong concurrency regression signal for requested-key eviction synchronization. Tests rely on sleeps and async scheduling, so timing failures are possible on constrained systems.
