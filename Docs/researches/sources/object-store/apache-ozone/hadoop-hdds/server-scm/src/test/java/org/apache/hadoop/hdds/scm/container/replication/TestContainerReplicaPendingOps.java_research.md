# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestContainerReplicaPendingOps.java

Purpose: This suite validates `ContainerReplicaPendingOps`, the in-memory tracker for scheduled replica ADD and DELETE commands. It checks scheduling, de-duplication, completion, expiration, metrics, subscriber notifications, and target-datanode scheduled-size accounting.

Important APIs and types: It uses `ContainerReplicaPendingOps`, `ContainerReplicaOp`, `ContainerReplicaPendingOpsSubscriber`, `ReplicationManagerMetrics`, `ReplicationManagerConfiguration`, `TestClock`, `ContainerID`, `DatanodeDetails`, `DatanodeID`, `ReplicateContainerCommand`, `DeleteContainerCommand`, `ReplicationType`, and the nested `SizeAndTime` scheduled-size value.

Control flow: Setup creates a test clock, pending-op tracker, metrics, datanodes, and commands. Tests schedule ADD/DELETE operations for different containers, query pending lists and counts, complete operations by type/index/datanode, remove specific ops, advance the clock to expire entries, and register mock subscribers to verify callbacks. Size tests inspect the `containerSizeScheduled` map as ADD ops are scheduled, completed, and expired.

State and persistence behavior: There is no persistence. State includes per-container pending-op lists, per-type and per-replication-type counts, metrics counters, subscriber list, deadlines, and a concurrent map from target datanode ID to scheduled container size and last update time. Expired ADDs are removed, while expired deletes are retained but still counted for timeout metrics.

Dependencies and integration points: Replication manager uses this tracker to avoid duplicate scheduling, process command completions, notify `MoveManager` or other subscribers, expose metrics, and account for in-flight size when picking targets.

Risks: Expiration semantics are nuanced: deadlines equal to current time are not removed until older, ADD and DELETE retention differs, and duplicate ADD scheduling replaces deadlines without subscriber notification. Metrics distinguish RATIS index 0 from EC nonzero indexes.

Test signals: Exact pending counts, duplicate replacement behavior, completion boolean return values, timeout metrics, created/deleted metrics, subscriber `opCompleted` calls with timeout flags, no notification for non-expired/replaced ops, and scheduled-size map updates/removals.
