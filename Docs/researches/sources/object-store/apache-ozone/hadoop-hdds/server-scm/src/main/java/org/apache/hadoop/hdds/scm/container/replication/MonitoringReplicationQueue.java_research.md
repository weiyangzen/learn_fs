# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/MonitoringReplicationQueue.java

Purpose: `MonitoringReplicationQueue` is a no-op `ReplicationQueue` used for read-only health checks. It allows the normal health-check chain to run without enqueueing under- or over-replicated containers for later command processing.

Important APIs and behavior: it overrides both `enqueue(UnderReplicatedHealthResult)` and `enqueue(OverReplicatedHealthResult)` with empty implementations.

Control flow: the class intentionally discards queue requests. It does not override dequeue methods, so inherited behavior remains irrelevant when used as a sink.

State and persistence: no state is stored and no queue entries persist. This protects read-only callers from side effects while still allowing reports to be updated.

Dependencies and integration: `ReplicationManager` keeps a `noOpsReplicationQueue` instance and uses it in `checkContainerStatus`, where a caller wants the same health classification as a monitor pass but no command work. It depends on `ContainerHealthResult` nested result types and `ReplicationQueue`.

Risks: this queue suppresses only enqueue side effects. Health handlers that send commands directly even in read-only mode would still be risky, so handler implementations must honor `ContainerCheckRequest.readOnly` separately. If future queue types add new enqueue overloads, this class must override them to preserve no-op semantics.

Test signals: coverage is indirect through read-only `ReplicationManager.checkContainerStatus` tests and health-check report tests that confirm status classification without queue growth or command dispatch.
