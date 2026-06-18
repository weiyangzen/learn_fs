# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/SCMPerformanceMetrics.java

Purpose: metrics source for SCM performance counters and latencies around delete-key and allocate-block operations.

Important APIs: static singleton `create`, `unRegister`, `getMetrics`, latency update methods, delete-key success/failure stats, block counters, and block getter methods.

Control flow and state: `create()` caches a static instance and registers it once. Updates compute elapsed nanoseconds using `Time.monotonicNowNanos()` and add to `MutableRate` fields; counters are mutable metrics fields.

Dependencies and integration: integrated with SCM block/key deletion and block allocation paths; uses Ozone metrics context.

Risks: `unRegister()` does not clear the static `instance`, so re-create after unregister may return an unregistered object. Direct construction relies on metrics injection for annotated fields. Tests should verify singleton lifecycle, latency updates with mocked start times, and block counter getters.
