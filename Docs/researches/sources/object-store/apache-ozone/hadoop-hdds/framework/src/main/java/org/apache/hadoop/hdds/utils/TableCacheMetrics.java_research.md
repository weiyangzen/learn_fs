# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/TableCacheMetrics.java

## Purpose
`TableCacheMetrics` exports cache size and hit/miss/iteration counters for a single HDDS table cache through Hadoop Metrics2.

## Important APIs and Types
`create(TableCache, tableName)` registers a metrics source named `<tableName>Cache`. `getMetrics` emits one `TableCacheMetrics` record tagged with the table name and gauges for size, hit count, miss count, and iteration count. `unregister` removes the source by the per-table name.

## Control Flow and State
The object stores references to the cache and table name. Metrics collection asks the cache for `CacheStats` and current size each time, so exported values reflect live cache state.

## Persistence, Dependencies, and Integration
No persistence exists. Dependencies include `TableCache`, `CacheStats`, `DefaultMetricsSystem`, and Metrics2. It integrates with typed table/cache implementations that want table-local cache observability.

## Risks and Test Signals
The registered source name differs from the record name (`SOURCE_NAME`), so consumers should validate both. Duplicate table names can collide in the metrics system. Tests should cover registration/unregistration, metric values from a fake cache, record tags, zero-counter state, and repeated registration behavior.
