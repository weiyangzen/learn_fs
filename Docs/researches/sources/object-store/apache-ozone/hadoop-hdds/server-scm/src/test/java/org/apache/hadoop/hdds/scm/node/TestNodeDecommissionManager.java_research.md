# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeDecommissionManager.java

Purpose: unit/integration tests for user-facing `NodeDecommissionManager` admin operations: host parsing, decommission, maintenance, recommission, leadership recovery, and safety checks for minimum available nodes.

Important APIs and types: setup creates a test SCM and real `SCMNodeManager`, mocked `ContainerManager`, `NodeDecommissionManager`, and allocation stubs producing mock `ContainerInfo` for Ratis or EC configs. Helpers create mock containers, inject container sets via `ScmNodeTestUtil`, simulate node-not-found behavior with a mocked node manager, and generate datanodes with unique, duplicate, and ambiguous host/port combinations.

Control flow: tests validate `HostDefinition` parsing and invalid ports; errors for missing hosts, wrong ports, and ambiguous host addresses; decommission/recommission by IP or `ip:port`; maintenance/recommission with expiry; rejection of transitions between decommission and maintenance workflows; `onBecomeLeader()` re-tracking nodes already in decommission/maintenance states; decommission safety failures for Ratis, EC, mixed Ratis+EC, not-in-service nodes, and node-not-found cases; maintenance safety failures and forced bypass for Ratis, EC, and mixed containers with configurable minimum replicas/redundancy.

State and persistence: uses temp SCM metadata through `HddsTestUtils.getScm`, real node manager state, mocked container metadata, datanode persisted operational state, and monitor tracked-node state. No commits or external services.

Integration points and risks: protects admin command semantics and cluster-safety validation before changing node op states. Risks include complex mock behavior that may not capture every real container-manager failure, static container ID counter shared across tests, and reliance on generated datanode addressing patterns.
