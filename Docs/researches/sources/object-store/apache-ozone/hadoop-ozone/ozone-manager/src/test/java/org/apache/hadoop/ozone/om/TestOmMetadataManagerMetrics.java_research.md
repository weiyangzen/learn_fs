# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOmMetadataManagerMetrics.java

Purpose: Regression tests for table-cache metrics registration conflicts when OM metadata tables are repeatedly initialized, especially during Recon-style synchronization.

Important APIs and types: `OmMetadataManagerImpl`, `TableCacheMetrics`, `Table`, `TableCache`, `CacheStats`, `DefaultMetricsSystem`, `MetricsSystem`, and `MetricsException`.

Control flow: setup creates a temp metadata manager; cleanup stops it and shuts down the metrics system. Tests repeatedly fetch the same table, fetch multiple tables, concurrently fetch tables from ten threads, manually unregister/reregister `TableCacheMetrics`, and simulate Recon reinitialization loops.

State and persistence: RocksDB table state is only indirectly involved. The primary state under test is Hadoop metrics source registration in `DefaultMetricsSystem` and table cache metrics lifecycle.

Dependencies and integration points: targets the table initializer path used by OM and Recon. It depends on metrics source naming convention `<tableName>Cache` and `TableCacheMetrics.create/unregister`.

Risks and edge cases: the helper `getRegisteredMetrics` is a weak proxy because it returns the metrics system rather than inspecting a source registry, so these tests mostly catch thrown exceptions rather than proving exact source identity. Concurrent reinitialization must not surface "already exists" metrics exceptions.

Test signals: no `MetricsException` during repeated/concurrent table access, non-null table and metrics handles, successful unregister/reregister for same source name, and a non-null metrics system after conflict resolution.
