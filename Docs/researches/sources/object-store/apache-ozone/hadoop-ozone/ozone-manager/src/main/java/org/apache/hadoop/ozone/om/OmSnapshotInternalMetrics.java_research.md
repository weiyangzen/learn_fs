# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmSnapshotInternalMetrics.java

Purpose: `OmSnapshotInternalMetrics` is a metrics2 source for internal snapshot maintenance operations, including purge, property updates, moving table keys, and snapshot defragmentation.

Important APIs and types: `create()` registers the metrics source, `unregister()` removes it. `MutableCounterLong` fields track operation and failure counts. Increment methods update purge/set-property/move-table-key counters and full/incremental defrag counters; getter methods expose counter values for tests and diagnostics.

Control flow: all methods are straightforward counter increments or reads. Some increment methods accept a `long count` for batched table-compaction or delta-file counts.

State and persistence: process-local metrics reset on restart. No DB or file persistence.

Dependencies and integration points: used by snapshot purge, snapshot property, move-table-key, and defrag services. Depends on Hadoop metrics2 annotations and `DefaultMetricsSystem`.

Risks: missing increments in maintenance services will make long-running snapshot work hard to diagnose. Counter-only metrics do not expose latency; latency is separately tracked in `OMPerformanceMetrics`.

Test signals: tests should register/unregister cleanly, assert each increment mutates only the intended counter, verify batch increments add exact counts, and ensure defrag success/failure/skipped paths are all instrumented.
