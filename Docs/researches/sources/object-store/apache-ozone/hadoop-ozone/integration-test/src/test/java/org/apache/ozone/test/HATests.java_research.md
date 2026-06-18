# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/HATests.java

Purpose: This abstract harness groups HA integration tests under one shared three-OM/three-SCM `MiniOzoneHAClusterImpl`.

Important APIs and types: It extends `ClusterForTests<MiniOzoneHAClusterImpl>`, uses `MiniOzoneCluster.newHABuilder`, random UUID-based OM/SCM service IDs, and nested suites including `TestOzoneFsHAURLs`, `TestStorageContainerManagerHAWithAllRunning`, `TestScmApplyTransactionFailure`, `TestGetClusterTreeInformation`, `TestDatanodeQueueMetrics`, and `TestScmAdminHA`.

Control flow: `newClusterBuilder` creates an HA builder from the common config, assigns random service IDs, and configures three OMs and three SCMs. The `TestCase` interface defines a `cluster()` method for nested HA suites. Each nested class extends an existing test and overrides `cluster()` to use the shared harness cluster.

State and persistence behavior: The harness owns shared HA cluster state. Nested tests exercise OM/SCM HA metadata, Ratis groups, datanode queues, cluster tree information, and filesystem HA URLs. Random service IDs prevent cross-run naming conflicts.

Dependencies and integration points: It links common cluster lifecycle to HA-specific tests across filesystem, SCM, OM, metrics, and shell admin areas. It also includes `TestScmAdminHA` from this subset as a nested command test.

Risks: HA tests can influence leadership, node state, and metrics for later nested tests. Shared cluster execution improves performance but makes ordering and cleanup more important. Random IDs improve isolation but can make logs less deterministic.

Test signals: Signals come from nested HA suites: URL resolution, SCM HA behavior, transaction failure handling, cluster-tree information, datanode queue metrics, and SCM admin roles command execution.
