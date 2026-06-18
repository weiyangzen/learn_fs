# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestMisReplicationHandler.java

Purpose: Abstract test harness for concrete Ratis and EC mis-replication handler tests. It centralizes setup, placement-policy stubbing, command capture, and shared assertions for `MisReplicationHandler.processAndSendCommands`.

Important APIs and types: Uses `MisReplicationHandler`, `ReplicationManager`, `ReplicationManagerMetrics`, `ReplicationConfig`, `ContainerInfo`, `ContainerReplica`, `ContainerReplicaOp`, `PlacementPolicy`, `ContainerPlacementStatus`, `ReplicateContainerCommand`, `SCMCommand`, `NodeStatus`, and `NodeSchemaManager`. Subclasses provide `getMisreplicationHandler` and `assertReplicaIndex`.

Control flow: `setup` creates a closed container from the supplied replication config, initializes topology schemas, mocks replication-manager config/metrics/node status/pending ops, and records commands from normal and throttled replication sends. `mockPlacementPolicy` returns an unsatisfied placement status. `testMisReplication` constructs a mocked `MisReplicatedHealthResult`, computes healthy in-service source replicas, asks the placement policy for replicas to copy, stubs `chooseDatanodes` to return expected targets, invokes the handler, and finally checks command count and command content in a `finally` block so exception paths still validate side effects.

State and persistence behavior: The harness is in-memory. Important state is the selected source set, remaining datanodes after copied replicas are removed, target datanodes, replica-index map, throttling boolean, captured commands, and metrics object. It does not persist container state or update SCM metadata.

Dependencies and integration points: Provides the integration layer between concrete handler implementations and common replication manager APIs. It also models placement-policy collaboration by asserting the used-node list passed to `chooseDatanodes` contains remaining replicas after selected sources are copied.

Risks and test signals: Risks include regressions hidden by duplicated subclass tests, incorrect source eligibility, wrong target selection inputs, and lost command assertions after exceptions. The harness gives strong shared signals: replicate command type, container ID, source membership, target membership, command count, and subclass-specific replica-index behavior.
