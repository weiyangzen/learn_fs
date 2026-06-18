<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerCacheMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerCacheMetrics.java

## Purpose

`ContainerCacheMetrics` registers Hadoop metrics for `ContainerCache` DB-handle activity: open/close latency, cache hits/misses, get/remove operations, and evictions. The complete 109-line file was read.

## Important APIs, Types, and Functions

The class is final and created through `create()`. It provides increment methods for DB get/remove, hits, misses, evictions, and latency samples, plus getters for the counter values.

## Control Flow

`create` registers a `ContainerCacheMetrics` source in the default metrics system. `ContainerCache` invokes the increment methods during get, miss/hit, open/close, and LRU removal paths.

## State and Persistence Behavior

Metrics are in-memory only and exported through Hadoop metrics. There is no explicit unregister method in this class.

## Dependencies and Integration Points

It uses `DefaultMetricsSystem`, `MetricsSystem`, `MutableRate`, and `MutableCounterLong`, and is held statically by `ContainerCache`.

## Risks and Edge Cases

The metrics source name is fixed, so repeated singleton resets in tests can hit duplicate registration problems. `incNumDbRemoveOps` exists but `ContainerCache.removeDB` does not call it in this source version.

## Test Signals

Tests should verify metrics registration, all counter increments, latency sample calls from cache open/close, and singleton/test lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerCacheMetrics.java -->
