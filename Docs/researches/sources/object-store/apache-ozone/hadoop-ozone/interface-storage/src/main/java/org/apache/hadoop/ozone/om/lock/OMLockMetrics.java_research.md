# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/OMLockMetrics.java

Purpose: Hadoop Metrics2 source for OM lock wait and hold time statistics.

Important APIs/types/functions: Static `create()` registers the source in `DefaultMetricsSystem`; `unRegister()` removes it. Setter methods add samples for read wait, read held, write wait, and write held times in milliseconds. Getter methods expose stat strings and latest max values. `getMetrics` snapshots all four `MutableStat`s into a metrics record.

Control flow, state, and persistence: Runtime metrics only. The object owns a `MetricsRegistry` and four `MutableStat`s. Samples are accumulated and exposed through Hadoop Metrics2; no DB persistence occurs.

Dependencies and integration points: Used by OM lock implementations via `IOzoneManagerLock.getOMLockMetrics()`. Depends on Hadoop metrics2, `DefaultMetricsSystem`, and Ozone metrics context.

Risks: Registration uses a fixed source name, so multiple registrations without unregistering can conflict. `lastStat().max()` depends on metrics snapshot state; callers should interpret longest values in relation to metrics intervals.

Test signals: No direct unit test in this subset. Metrics behavior is typically verified in lock implementation or metrics integration tests.
