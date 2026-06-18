# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/cache/TestTableCache.java

Purpose: Parameterized unit tests for table cache implementations: full cache, partial cache, and no-cache behavior.

Important APIs/types/functions: `TableCache`, `FullTableCache`, `PartialTableCache`, `TableNoCache`, `CacheKey`, `CacheValue`, `CacheStats`, `evictCache`, `getEpochEntries`, `iterator`, `size`, and `TableCache.CacheType`.

Control flow: Tests create cache instances by type, populate epoch-indexed entries, evict selected epochs, verify full-cache no-op/retention rules versus partial-cache deletion rules, handle renamed keys and overrides, process delete tombstones, run asynchronous writes, validate nonconsecutive epoch lists, inspect stats counters, and assert no-cache ignores writes.

State and persistence behavior: All state is in-memory cache state. Epoch maps model cleanup state used by HA transaction application and cache compaction.

Dependencies and integration points: Uses JUnit parameterization, `CompletableFuture`, `GenericTestUtils` log-level changes, and cache internals exposed through stats and epoch accessors.

Risks: Tests rely on implementation-specific epoch-entry sizes. Parallel write coverage is limited to simple asynchronous insertion and not a full race detector.

Test signals: Strong cache semantics signal for eviction, overridden entries, tombstones, stats, full versus partial behavior, and no-cache null behavior.
