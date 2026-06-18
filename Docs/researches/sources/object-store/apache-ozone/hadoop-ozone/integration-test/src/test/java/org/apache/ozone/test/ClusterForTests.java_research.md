# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/ClusterForTests.java

Purpose: This generic base class manages lifecycle and common configuration for integration tests that share a `MiniOzoneCluster` instance across nested test suites.

Important APIs and types: It uses `MiniOzoneCluster`, `OzoneConfiguration`, `DatanodeRatisServerConfig`, `RatisClientConfig.RaftConfig`, `OzoneClientConfig`, `IOUtils`, JUnit `@BeforeAll`, `@AfterAll`, and `@TestInstance(PER_CLASS)`.

Control flow: `createBaseConfiguration` sets shorter Ratis request/watch timeouts, disables stream buffer flush delay, enables HBase enhancements, hsync, client HBase enhancements, and sets OM lease soft limit to zero. Subclasses can override `createOzoneConfig`, `newClusterBuilder`, `createCluster`, and `onClusterReady`. `startCluster` creates the cluster, waits for readiness, and calls the hook; `shutdownCluster` closes it quietly.

State and persistence behavior: The class owns a single cluster field for the test instance. Persistent state is whatever the mini cluster creates and what nested tests write. Configuration objects are created before cluster startup and applied through builders.

Dependencies and integration points: It is the foundation for `NonHATests`, `HATests`, `FreonTests`, and `AclTests`, and centralizes client/server timeout and hsync settings used by many integration suites.

Risks: Shared cluster state can cause interactions between nested tests. PER_CLASS lifecycle means subclasses must avoid relying on per-test cluster recreation. The default builder uses five datanodes unless subclasses override it.

Test signals: This file has no direct tests; its signal is successful startup, readiness, optional hook execution, and quiet shutdown for subclasses.
