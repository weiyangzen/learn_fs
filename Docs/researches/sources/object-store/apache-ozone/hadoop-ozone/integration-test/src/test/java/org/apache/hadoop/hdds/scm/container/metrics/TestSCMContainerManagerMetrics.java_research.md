<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/metrics/TestSCMContainerManagerMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/metrics/TestSCMContainerManagerMetrics.java

Purpose: Verifies metrics emitted by `SCMContainerManagerMetrics` for container create/delete/list operations and report processing.

Important APIs and types: Uses `NonHATests.TestCase`, `SCMContainerManagerMetrics`, `ContainerManager`, `ContainerInfo`, `ContainerID`, `RatisReplicationConfig`, `ECReplicationConfig`, `ContainerNotFoundException`, `OzoneTestUtils.closeAllContainers`, and metrics helpers.

Control flow: The first test samples initial counters, successfully allocates a Ratis one container, attempts unsupported EC(8,5) allocation, deletes the valid container, attempts deletion of a random missing container, and lists containers. The second test verifies full container reports have already been processed, closes all containers, creates keys, and waits for successful ICR report counter growth.

State and persistence behavior: Container manager state changes through allocate and delete operations. Metrics persist in the running process and are sampled before and after operations. Report metrics reflect asynchronous datanode report processing.

Dependencies and integration points: Integrates SCM container manager, replication config validation, event queue container close helper, object-store key creation, datanode ICR reporting, and Hadoop metrics.

Risks: Metrics are cluster-global, so tests compare deltas rather than absolute values. ICR progress depends on asynchronous reports after key creation. Random missing container IDs are chosen in a narrow range but expected not to exist.

Test signals: Signals include successful-create increment, failure-create increment without successful-create change, successful-delete increment, failure-delete increment without successful-delete change, list-operation increment, positive full report count, and ICR success count increasing after test data creation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/metrics/TestSCMContainerManagerMetrics.java -->
