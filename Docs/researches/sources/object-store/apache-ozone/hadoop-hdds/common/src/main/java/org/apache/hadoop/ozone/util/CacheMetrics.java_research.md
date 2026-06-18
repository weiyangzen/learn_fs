# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/CacheMetrics.java

## Purpose

`CacheMetrics` is a reusable Hadoop metrics2 `MetricsSource` for publishing Guava cache statistics.

## APIs and control flow

`create(Cache, Object)` derives a source name from the owner class and identity hash; `create(Cache, String)` registers a new source with `DefaultMetricsSystem`. `getMetrics` emits a record tagged by cache name and gauges for size, hit/miss counts and rates, load success/exception counts, and eviction count. `unregister()` removes the source by the generated source name.

## State, dependencies, and integration

State is the observed `Cache`, display name, and metrics source name. Dependencies include Guava cache stats, Hadoop metrics2, `DefaultMetricsSystem`, and Ratis `JavaUtils`. It integrates with services that need cache observability without writing custom metrics sources.

## Risks and test signals

Metrics source names include object hash codes for owner-based creation; repeated registration for the same owner string can collide or fail depending on metrics-system behavior. Cache stats require Guava caches created with `recordStats()`. Tests should cover registration/unregistration, emitted gauge names, and behavior with caches that do not record stats.
