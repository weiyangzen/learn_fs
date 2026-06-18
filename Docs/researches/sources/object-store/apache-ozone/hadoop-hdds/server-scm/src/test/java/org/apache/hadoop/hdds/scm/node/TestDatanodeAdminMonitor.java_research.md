# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestDatanodeAdminMonitor.java

Purpose: isolated unit tests for `DatanodeAdminMonitorImpl`, covering decommission and maintenance workflow state transitions without requiring a full live SCM.

Important APIs and types: setup creates `SimpleMockNodeManager`, mocked `ReplicationManager`, `EventQueue`, a `START_ADMIN_ON_NODE` counting handler, and `NodeDecommissionMetrics`. Tests use `DatanodeAdminMonitorTestUtil` to mock Ratis/EC `ContainerReplicaCount` and replication health. Helper `generateContainers()` creates container ID sets; `getFirstTrackedNode()` inspects monitor tracking state.

Control flow: tests cover queue/cancel counters; decommission start event and pipeline closure gating; immediate decommission when no containers/pipelines exist; waiting for under-replicated containers; special handling of quasi-closed unhealthy replicas with unique origins; ignoring deleting containers; EC unrecoverable replica replacement; aborts when decommissioning nodes return to unexpected state or dead health; start-time tracking; maintenance transition to `IN_MAINTENANCE`, expiry back to `IN_SERVICE`, expiry while closing pipelines or replicating containers, dead maintenance nodes staying tracked, cancellation to `IN_SERVICE`, and pending replication API categories.

State and persistence: all state is in memory: mock node statuses, container sets, monitor queues/tracked nodes, metrics, and event queue. No database or filesystem is used.

Integration points and risks: verifies the monitor contract with `NodeManager`, `ReplicationManager`, metrics, and SCM events. It is broad but mock-heavy; correctness depends on `DatanodeAdminMonitorTestUtil` accurately modeling replication-manager responses. Timing-sensitive maintenance expiry is simulated by setting expiry in the past.
