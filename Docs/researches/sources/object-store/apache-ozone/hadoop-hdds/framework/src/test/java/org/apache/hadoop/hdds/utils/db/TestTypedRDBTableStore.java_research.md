# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestTypedRDBTableStore.java

Purpose: Tests `TypedTable<String,String>` behavior over `RDBTable`, especially cache-overlay semantics and typed CRUD.

Important APIs/types/functions: `TypedTable`, `StringCodec`, `ByteArrayCodec`, `TableCache.CacheType.PARTIAL_CACHE`, `CacheKey`, `CacheValue`, `addCacheEntry`, `cleanupCache`, `iterator`, `putWithBatch`, `deleteWithBatch`, `isExist`, `getIfExist`, and `getEstimatedKeyCount`.

Control flow: Setup creates ten column families. Tests verify typed put/get/empty, delete, batch put/delete, iterator/foreach counts, exception translation from raw `RDBTable.iterator`, cache reads for synthetic entries, cache tombstone handling, cache cleanup by epoch, existence/get-if-exists with and without cache entries, estimated counts, and byte-array typed table copy semantics.

State and persistence behavior: Real RocksDB state backs typed tables, while `addCacheEntry` injects in-memory overlay values or tombstones. Cleanup removes cache epochs and waits for expected size changes.

Dependencies and integration points: Uses RocksDB managed options, HDDS cache classes, Mockito for exception translation, and `GenericTestUtils.waitFor`.

Risks: Static iterator `count` is shared across tests. A loop in `testTypedTableWithCache` always reads key `"1"` instead of the loop key, narrowing coverage. Cache tests are sensitive to epoch cleanup implementation details.

Test signals: Good signal for typed table CRUD, batch delegation, cache overlay precedence, tombstone behavior, cleanup, exception wrapping, and byte-array defensive-copy semantics.
