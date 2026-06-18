# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/OzoneManagerDoubleBufferMetrics.java

## Purpose
`OzoneManagerDoubleBufferMetrics` publishes Hadoop metrics for double-buffer flush activity.

## Important APIs and Types
It is a singleton metrics source registered with `DefaultMetricsSystem`. Metrics include total flush operations, total flushed transactions, max transactions per flush iteration, RocksDB batch commit latency (`MutableRate`), average transactions per iteration (`MutableGaugeFloat`), and queue size (`MutableStat`). `updateFlush` updates the aggregate counters and gauges after a flush.

## Control Flow
`create` registers a singleton if none exists. `updateFlush` increments operation and transaction counters, recomputes average transaction count, raises the max counter if needed, and records queue size. `updateFlushTime` records commit latency. `unRegister` unregisters the source name.

## State and Persistence Behavior
Metrics state is in-memory in the Hadoop metrics system and is not persisted. It represents runtime observability for OM double-buffer flushes.

## Dependencies and Integration Points
`OzoneManagerDoubleBuffer` creates and updates this source. Tests can read getters or internal package-private metric objects.

## Risks and Edge Cases
The singleton is static. Multiple OM instances in the same JVM can share one metrics object unless unregistered carefully. `setMaxNumberOfTransactionsFlushedInOneIteration` uses `Math.negateExact` on the current value; overflow is unlikely but possible in theory for extremely large counters.

## Test Signals
Tests should verify singleton registration, flush counter increments, max update logic, average calculation, queue stat updates, and unregister behavior.
