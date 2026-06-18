<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerEventHandler.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerEventHandler.java

Purpose: validates the event adapter that reacts to datanode events by waking `ReplicationManager` only when SCM is leader-ready and not in safe mode.

Important APIs and types: `ReplicationManagerEventHandler`, `ReplicationManager.notifyNodeStateChange`, `SCMContext.isLeaderReady`, `SCMContext.isInSafeMode`, `EventPublisher`, and `DatanodeDetails`.

Control flow: a parameterized `MethodSource` enumerates four leader/safe-mode combinations. The test stubs SCM context, sends a random datanode message through `onMessage`, and verifies whether `notifyNodeStateChange()` was called exactly once or not at all.

State and persistence behavior: no persistence. The observable state is the mocked leader/safe-mode gate and invocation count.

Dependencies and integration points: integrates SCM HA state with replication-manager scheduling. The `EventPublisher` is passed through but not used by the asserted behavior.

Risks: the test intentionally covers only the gate, not event payload content or publisher interactions. Any future requirement to react to specific datanode identities would need added coverage.

Test signals: compact truth-table coverage confirms the handler wakes replication work only for active, non-safe-mode SCM leadership.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerEventHandler.java -->
