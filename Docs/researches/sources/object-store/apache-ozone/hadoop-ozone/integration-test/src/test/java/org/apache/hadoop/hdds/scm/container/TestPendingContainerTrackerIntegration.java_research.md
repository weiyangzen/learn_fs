<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/TestPendingContainerTrackerIntegration.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/TestPendingContainerTrackerIntegration.java

Purpose: Integration tests for `PendingContainerTracker`, proving container allocation records pending containers and incremental container reports remove them while metrics advance.

Important APIs and types: Uses `MiniOzoneCluster`, `ContainerManager`, `SCMNodeManager`, `PendingContainerTracker`, `SCMNodeMetrics`, `OzoneClient`, `OzoneBucket`, `OzoneOutputStream`, and `RatisReplicationConfig`.

Control flow: Setup configures slower full container reports, faster heartbeat interval, small container size, one container per owner and per metadata disk, and three datanodes. It validates the node manager exposes a pending tracker and captures its metrics. Tests allocate containers directly or write keys, then use `GenericTestUtils.waitFor` to observe added and removed counters increasing.

State and persistence behavior: Cluster state includes allocated containers and keys written through the object-store client. Pending-container state is maintained in SCM node-manager runtime state and removed when datanodes report the container through ICR processing. Metrics are the observed state contract.

Dependencies and integration points: Bridges SCM allocation, node pending tracking, datanode heartbeats/ICRs, object-store key creation, and SCM node metrics.

Risks: The comments and log message mention shorter intervals than the configured values, which can mislead maintainers. The five-second waits are tight for integration environments. Metrics are cumulative and only checked for increases, so the test validates lifecycle activity rather than exact pending set contents.

Test signals: Signals are non-null pending tracker and metrics, `NumPendingContainersAdded` increasing after allocation/key creation, `NumPendingContainersRemoved` increasing after ICR processing, and successful key writes that cause datanode reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/TestPendingContainerTrackerIntegration.java -->
