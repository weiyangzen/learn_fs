# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/CacheStats.java

## Purpose

`CacheStats` is an immutable snapshot of table cache hit, miss, and iteration counters. The complete 45-line source was read for this report.

## Important APIs, Types, and Functions

The constructor accepts `cacheHits`, `cacheMisses`, and `iterationTimes`. Getters return each count.

## Control Flow

There is no control flow beyond construction and getters.

## State and Persistence Behavior

It is an in-memory metrics snapshot. It does not reset counters or persist metrics.

## Dependencies and Integration Points

It is produced by `CacheStatsRecorder` and returned by `TableCache.getStats`, then exposed through `TableCacheMetrics`.

## Risks and Edge Cases

The class performs no validation against negative values. Snapshot freshness depends on the recorder.

## Test Signals

Tests should verify snapshot values through cache get/lookup/iterator operations and metrics source integration.
