# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/QuasiClosedStuckOverReplicationHandler.java

Purpose: `QuasiClosedStuckOverReplicationHandler` removes excess replicas from Ratis containers that are quasi-closed stuck, where multiple origin datanodes may represent diverged histories. It preserves configured copy counts per origin rather than treating all replicas as equivalent.

Important APIs and behavior: `processAndSendCommands` skips work when any delete is already pending, filters stale/dead replicas by requiring node health `HEALTHY`, constructs `QuasiClosedStuckReplicaCount` with configured best-origin and other-origin copy targets, gets over-replicated origins, sorts each origin's removable replicas deterministically, and sends forced throttled delete commands with replica index `0`.

Control flow: for each mis-replicated origin, it deletes `replicaDelta` replicas from the sorted source list. It records the first `CommandTargetOverloadedException` but continues trying other deletes. If any overloaded exception occurred, it increments partial replication metrics when some commands were sent and rethrows to requeue.

State and persistence: no local persistence. Delete commands are tracked by `ReplicationManager`. The handler uses metrics for partial cleanup.

Dependencies and integration: it depends on `ReplicationManager` for node status, config, delete throttling, and metrics; `QuasiClosedStuckReplicaCount` for origin-aware redundancy; and `QuasiClosedStuckReplicationCheck.shouldHandleAsQuasiClosedStuck` through `ReplicationManager` routing.

Risks: the handler assumes `origin.getSources()` has at least `replicaDelta` entries; the count object currently constructs deltas from set sizes, so this should hold. Filtering out non-healthy datanodes can delay deletion until node state stabilizes. Sorting by `hashCode` gives deterministic deletion but does not prefer lower BCSID within an overfull origin.

Test signals: `TestQuasiClosedStuckOverReplicationHandler` and `TestQuasiClosedStuckReplicaCount` cover pending-delete suppression, origin target counts, deterministic deletes, overload handling, and partial metrics.
