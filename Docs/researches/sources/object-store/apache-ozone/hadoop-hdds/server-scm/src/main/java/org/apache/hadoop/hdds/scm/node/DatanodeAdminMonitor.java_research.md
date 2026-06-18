# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/DatanodeAdminMonitor.java

Purpose: `DatanodeAdminMonitor` defines the monitor contract for decommission, recommission, and maintenance workflows. It is a `Runnable` so `NodeDecommissionManager` can schedule periodic workflow ticks.

Important APIs and types: The interface exposes `startMonitoring`, `stopMonitoring`, `getTrackedNodes`, `setMetrics`, and `getContainersPendingReplication`. Its current tracked-node type is the implementation class `DatanodeAdminMonitorImpl.TrackedNode`, and pending-container output is keyed by strings such as `UnderReplicated` and `UnClosed`.

Control flow: Implementations accept nodes into a monitored workflow, queue cancellation/recommission requests, update metrics, and answer progress queries. The actual periodic behavior is implemented by `DatanodeAdminMonitorImpl.run`.

State and persistence behavior: The interface defines no state, but implementers maintain in-memory workflow queues and snapshots. Workflow progress is reflected through node operational state in `NodeManager`; durable recovery relies on datanodes re-registering their persisted operational state and the decommission manager resuming monitoring.

Dependencies and integration points: It couples node administration to `DatanodeDetails`, `ContainerID`, `NodeDecommissionMetrics`, and `NodeNotFoundException`. It is owned by `NodeDecommissionManager` and observed by CLI/JMX-style progress calls.

Risks: Exposing `DatanodeAdminMonitorImpl.TrackedNode` in the interface leaks the implementation. The `Map<String, List<ContainerID>>` return shape is stringly typed, so callers must know exact category names.

Test signals: Contract tests should verify that starting, stopping, tracking, metrics assignment, and pending-replication queries behave consistently through the interface, not only the concrete monitor.
