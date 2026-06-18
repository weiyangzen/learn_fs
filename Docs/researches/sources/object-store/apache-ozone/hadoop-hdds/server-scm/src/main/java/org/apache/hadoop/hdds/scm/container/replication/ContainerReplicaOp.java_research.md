# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerReplicaOp.java

Purpose: immutable descriptor for a pending replica ADD or DELETE operation.

Important APIs: constructor, getters for op type, target, replica index, command, deadline epoch millis, container size, and enum `PendingOpType`.

Control flow and state: no internal mutation; all pending-op lifecycle state is managed by `ContainerReplicaPendingOps`. The command may be nullable.

Dependencies and integration: stored by pending ops, passed to subscribers like `MoveManager`, and used by ReplicationManager tests to assert scheduled operations.

Risks: no equals/hashCode, so duplicate detection must compare fields manually as pending ops does. Deadline semantics rely on caller-provided clock values. Test signals should cover ADD/DELETE tracking, EC replica indexes, command retention, and size accounting for ADD ops.
