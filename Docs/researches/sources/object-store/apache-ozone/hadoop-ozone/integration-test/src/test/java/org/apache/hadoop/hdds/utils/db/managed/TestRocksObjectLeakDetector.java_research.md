# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/utils/db/managed/TestRocksObjectLeakDetector.java

Purpose: manual/unhealthy integration test for managed RocksDB object leak detection metrics. It intentionally creates leaked managed Rocks objects and expects cluster shutdown to fail because leaked objects remain.

Important APIs/types/functions: `setUp`, `cleanUp`, `testLeakDetector`, generic `testLeakDetector(Supplier<T>)`, and `allocate`. It exercises many managed wrappers: `ManagedBloomFilter`, `ManagedColumnFamilyOptions`, `ManagedEnvOptions`, `ManagedFlushOptions`, `ManagedIngestExternalFileOptions`, `ManagedLRUCache`, `ManagedOptions`, `ManagedReadOptions`, `ManagedSlice`, `ManagedStatistics`, `ManagedWriteBatch`, and `ManagedWriteOptions`.

Control flow: setup enables RocksDB statistics (`OZONE_METADATA_STORE_ROCKSDB_STATISTICS=ALL`) and starts a MiniOzoneCluster. The test iterates wrapper suppliers. For each type, it snapshots total managed objects and leak objects, allocates and closes one object, runs GC and sleeps for leak detector background processing, then expects total object count to increase but leak count unchanged. It then allocates another object without closing it, runs GC/sleeps again, and expects both total object count and leak count to increase. Cleanup asserts that `cluster.shutdown()` throws `AssertionError`, matching the intentional leak behavior.

State and persistence: process-global `ManagedRocksObjectMetrics.INSTANCE` counters, native RocksDB object lifetimes, GC/finalizer/leak detector timing, and MiniOzoneCluster resources. The leaked objects are intentionally not closed.

Dependencies and integration points: managed RocksDB wrappers, Ozone metadata store statistics, JUnit `@Unhealthy`, MiniOzoneCluster, JVM GC behavior, and leak detector background tasks.

Risks: explicitly documented as manual-only and flaky because background processes can allocate additional managed Rocks objects, invalidating exact counter deltas. Sleep-based timing and GC are nondeterministic. Running it with normal suites can poison later tests by leaving leak metrics and leaked native objects.

Test signals: exact counter assertions for total managed objects and leak objects, plus expected shutdown `AssertionError`.
