# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeDecommissionMetrics.java

Purpose: verifies `NodeDecommissionMetrics` reflects `DatanodeAdminMonitorImpl` workflow state for decommission, maintenance, recommission, pipelines, and container replication categories.

Important APIs and types: setup creates `SimpleMockNodeManager`, mocked `ReplicationManager`, monitor, event queue, `START_ADMIN_ON_NODE` handler, and metrics via `NodeDecommissionMetrics.create()`. Teardown unregisters metrics. Tests use `DatanodeAdminMonitorTestUtil.mockGetContainerReplicaCount()` to control container health classifications.

Control flow: tests start monitoring datanodes in entering maintenance or decommissioning states, call `monitor.run()`, and assert totals plus host-specific metric getters. Covered counters include tracked decommissioning/maintenance nodes, recommission nodes, pipelines waiting to close, under-replicated containers, sufficiently replicated containers, unclosed containers, aggregation across multiple datanodes, and workflow start time bounds.

State and persistence: all state is in-memory monitor/node-manager state and registered metrics. Metrics registration is process-global enough that `unRegister()` in teardown is important to prevent leakage between tests.

Integration points and risks: this is the observability companion to admin monitor tests, ensuring admin progress can be scraped and attributed by host. Mocked replication responses mean metric correctness is tested after classification inputs are supplied, not the full replication classification algorithm itself.
