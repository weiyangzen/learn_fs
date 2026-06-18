<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerScenarios.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerScenarios.java

Purpose: provides a JSON-driven scenario harness for replication-manager health checks and command execution. It lets resource files describe containers, replicas, pending operations, expected report counters, queue sizes, and expected commands.

Important APIs and types: `Scenario`, `TestReplica`, `PendingReplica`, `ExpectedCommands`, `Expectation`, `ReplicationManager`, `ReplicationQueue`, `ReplicationManagerReport`, `ContainerReplicaPendingOps`, Jackson `ObjectMapper` / `MappingIterator`, `NodeStatus`, `DatanodeDetails`, `DatanodeID`, and command type `SCMCommandProto.Type`.

Control flow: `@BeforeAll` loads every JSON file under `/replicationManagerTests`, rejects duplicate descriptions per file, and stores resource names for diagnostics. Each parameterized test creates a fresh mocked SCM environment, applies scenario maintenance settings, builds `ContainerInfo`, schedules pending ops, builds replicas, runs `processContainer`, checks report and queue expectations, checks read-only `checkContainerStatus` emits no commands, then processes one queued under- or over-replicated result and checks repair commands.

State and persistence behavior: scenario aliases create stable in-test datanode and origin identities through static maps cleared before each test. `NODE_STATUS_MAP` models datanode operational and health states. Pending operations are scheduled into a real `ContainerReplicaPendingOps`; no durable store is touched.

Dependencies and integration points: integrates test resources, Jackson deserialization, simple test placement policies, `NodeManager` command capture, SCM context leadership/safe-mode gating, and command-count mocks. It is the bridge between human-readable replication scenarios and `ReplicationManager` behavior.

Risks: the class comment notes scenario support does not cover mis-replicated containers. Static alias maps require careful clearing to avoid cross-scenario leakage. JSON field setters define the external scenario schema, so renaming setters changes resource compatibility.

Test signals: broad data-driven coverage across many container/replica combinations, including check-phase commands, read-only status checks, queue sizes, and execution-phase commands. Failures include scenario resource names and descriptions, making regressions traceable to the JSON case.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerScenarios.java -->
