<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerMetrics.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerMetrics.java

Purpose: verifies that `ReplicationManagerMetrics` exposes gauges for container lifecycle states and replication health states based on `ReplicationManagerReport`.

Important APIs and types: `ReplicationManagerMetrics.create`, `ReplicationManagerReport`, `HddsProtos.LifeCycleState`, `ContainerHealthState`, `MetricsAsserts.getMetrics`, and `getLongGauge`.

Control flow: setup builds a report with deterministic counts by incrementing lifecycle states according to proto numbers and health states according to enum ordinals. The mocked manager returns config, report, pending ops, and a real queue, then metrics are registered. Tests read gauges by metric name and compare expected values.

State and persistence behavior: metrics are registered in the process metrics system and unregistered in `@AfterEach` to prevent leakage. The report is the source of gauge state.

Dependencies and integration points: ties report accounting to the Hadoop/Ozone metrics source named by `ReplicationManagerMetrics.METRICS_SOURCE_NAME`.

Risks: metric-name compatibility is critical; renaming `ContainerHealthState.getMetricName()` or lifecycle gauge names will break consumers and these tests. Metrics registration lifecycle must remain isolated.

Test signals: confirms all lifecycle gauges and every `ContainerHealthState` gauge are present with expected values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerMetrics.java -->
