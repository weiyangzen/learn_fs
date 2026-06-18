<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHAMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHAMetrics.java

Purpose: This test verifies the leader-state metric exposed by `SCMHAMetrics`.

Important APIs and types: It uses `SCMHAMetrics.create`, `getMetrics`, `getSCMHAMetricsInfoLeaderState`, `MetricsCollectorImpl`, and random SCM node IDs from `RandomStringUtils`.

Control flow: One test creates metrics with local node ID equal to leader ID and expects leader state `1`. The other creates metrics with a different leader ID and expects leader state `0`. `AfterEach` unregisters the metrics source.

State and persistence behavior: State is runtime metrics registration and current leader/local SCM IDs. No persistence.

Dependencies and integration points: This guards SCM HA metrics consumed by monitoring systems to identify whether an SCM instance is leader or follower.

Risks: The static metrics registration must be cleaned up to avoid cross-test pollution.

Test signals: Exact metric integer values for leader and follower modes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHAMetrics.java -->
