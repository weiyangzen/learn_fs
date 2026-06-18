<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeUtil.java

Purpose: Provides shared helper methods for SCM node integration tests to wait for operational, health, and persisted datanode states and to format datanode host/port strings.

Important APIs and types: Exposes `waitForDnToReachOpState`, `waitForDnToReachHealthState`, `getNodeStatus`, `getDNHostAndPort`, and `waitForDnToReachPersistedOpState`. Uses `NodeManager`, `NodeStatus`, `DatanodeDetails`, `HddsProtos.NodeOperationalState`, `HddsProtos.NodeState`, JUnit assertions, and `GenericTestUtils.waitFor`.

Control flow: Wait helpers poll every 200 ms for up to 30 seconds. `getNodeStatus` wraps `nodeManager.getNodeStatus` in `assertDoesNotThrow` to make lambdas fail with assertion context rather than checked exceptions. `getDNHostAndPort` returns hostname plus the first registered datanode port.

State and persistence behavior: The helper itself has no durable state. It observes SCM runtime `NodeStatus` and datanode-side persisted operational state stored on the mutable `DatanodeDetails` object.

Dependencies and integration points: Used by decommission, maintenance, and replication-manager integration tests. It standardizes polling intervals and CLI address formatting for `ContainerOperationClient` node admin calls.

Risks: Persisted-state waiting checks the supplied object, so callers must pass a `DatanodeDetails` instance that will be updated by the code under test. `getDNHostAndPort` assumes `getPorts().get(0)` is valid and appropriate for admin commands.

Test signals: Consumers rely on these helpers for timeout-based confirmation of health, operational state, persisted datanode operational state, and stable host:port identifiers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeUtil.java -->
