# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestDeadNodeHandler.java

Purpose: integration and race-regression tests for `DeadNodeHandler` and related `HealthyReadOnlyNodeHandler` topology behavior.

Important APIs and types: setup builds a real test `StorageContainerManager`, obtains `SCMNodeManager`, `PipelineManagerImpl`, and `ContainerManager`, sets SCM context leader/safemode status, injects a mock Ratis pipeline provider, and creates a `DeadNodeHandler` with mocked `DeletedBlockLog`. Helpers set node health state, register container IDs on datanodes through `ScmNodeTestUtil`, and register container replicas.

Control flow: `testOnMessage()` registers datanodes with storage and metadata reports, exits safemode, waits for pipelines, allocates containers, assigns replicas, and then exercises dead handling first for an `IN_MAINTENANCE` node and then an `IN_SERVICE` node. It asserts topology removal, replication-manager notification suppression or firing, deleted-block callbacks, command queue cleanup, and replica removal behavior. Other tests cover skipping topology removal when the node has resurrected to `HEALTHY_READONLY`, unconditionally re-adding removed healthy-readonly nodes, and a controlled thread interleaving where `DeadNodeHandler` blocks before topology removal while the node resurrects.

State and persistence: uses temp SCM metadata, live in-memory topology, container state, pipeline state, command queues, and mocked deleted-block log. Threading tests use latches and a spawned thread.

Integration points and risks: protects dead-node cleanup, replication notification, topology consistency, and resurrection races. `testOnMessage` is marked flaky, indicating timing/environment sensitivity around pipeline creation and full SCM setup.
