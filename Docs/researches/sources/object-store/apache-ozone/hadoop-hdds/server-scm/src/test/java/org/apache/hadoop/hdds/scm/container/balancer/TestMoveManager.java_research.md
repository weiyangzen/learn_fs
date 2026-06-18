# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestMoveManager.java

Purpose: This suite validates `MoveManager`, the balancer component that turns a requested container move into a low-priority replication command followed by a forced delete from the source. It checks preflight rejection, asynchronous completion, timeout handling, EC replica indexes, and the optional ability to move non-standard containers.

Important APIs and types: It mocks `ReplicationManager` and `ContainerManager`, and asserts `MoveManager.MoveResult` values including node health failures, in-flight op failures, replication/delete timeouts, policy failures, and `COMPLETED`. It uses `ContainerReplicaOp` ADD/DELETE events, `ContainerHealthResult`, `NodeStatus`, `TestClock`, `ContainerInfo`, `ContainerReplica`, `RatisReplicationConfig`, `ECReplicationConfig`, and `ReplicationTestUtil`.

Control flow: Setup creates a closed RATIS container, replica set, node-status map, pending-op list, and mocked health checks. Tests call `move`, inspect immediate future results for rejected moves, or drive the normal two-stage path by invoking `opCompleted` for ADD and DELETE operations. Helper `setupSuccessfulMove` verifies that the replicate command is sent, while `completeMove` simulates successful add and delete completion.

State and persistence behavior: There is no on-disk state. Runtime state includes the active move future, source/target datanodes, replica set mutation, pending operation list, node status map, clock-derived deadlines, and `includeNonStandardContainers` / timeout configuration inside `MoveManager`.

Dependencies and integration points: The test models integration with replication health checks, pending replica operation tracking, command dispatch to datanodes, container metadata lookup, and balancer rules for CLOSED, QUASI_CLOSED, over-replicated, and EC containers.

Risks: Many assertions depend on mocked replica sets and future completion rather than real datanode reports. Source replica selection uses set iteration in helpers. Deadline behavior is sensitive to replication timeout, move timeout, and the default datanode timeout offset.

Test signals: Signals include exact `MoveResult` values, no duplicate active move, replicate/delete command verification with replica indexes, future completion after callbacks, delete suppression when the source replica disappears, policy rejection before deleting an unsafe source, and successful QUASI_CLOSED/over-replicated moves only when enabled.
