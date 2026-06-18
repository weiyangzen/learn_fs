# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestStatisticsUpdate.java

Purpose: verifies that node statistics in `NodeManager` are updated from node reports and adjusted when a datanode becomes dead.

Important APIs and types: uses real SCM from `HddsTestUtils.getScm`, `NodeReportHandler`, `DeadNodeHandler`, `SCMNodeStat`, `SCMNodeMetric`, `NodeReportFromDatanode`, `PipelineManager`, and SCM events.

Control flow: setup creates an SCM with short heartbeat/stale/dead intervals, obtains its node manager, and registers a `DeadNodeHandler` on a local event queue. The test registers two datanodes with storage reports, sends both reports through `NodeReportHandler`, verifies aggregate and per-node stats, then heartbeats only the second datanode until the first ages out. Final assertions show aggregate stats contain only the surviving node.

State and persistence behavior: state is the live SCM node manager state. Node reports add per-node and aggregate stat entries; heartbeat timing moves one node out of active accounting. The test does not explicitly close SCM in this class, so lifecycle is inherited from the test harness/object reachability.

Dependencies and integration points: integrates node reports, heartbeat health transitions, dead-node handling, SCM event constants, and mocked pipeline manager behavior for dead-node processing.

Risks and edge cases: uses sleeps around one-second stale/dead intervals, so it can be timing-sensitive. The comment notes missing direct logic to mark a node dead in `NodeManager`, so the test simulates it by heartbeat omission. The local `EventQueue` handler is configured but report handling uses mocked publishers.

Test signals: confirms stat aggregation from multiple datanodes, per-node stat retrieval, and aggregate removal of dead-node capacity/usage.
