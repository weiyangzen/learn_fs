# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ECOverReplicationHandler.java

Purpose: `ECOverReplicationHandler` fixes EC containers with duplicate healthy in-service copies of the same replica index. It sends delete commands only when removal will not drop an EC index to zero.

Important APIs and behavior: `processAndSendCommands` is the entry point. It filters input replicas to datanodes whose `NodeStatus` is healthy and whose operational state is `IN_SERVICE`, creates `ECContainerReplicaCount`, checks current and future over-replication with and without pending deletes, selects delete candidates through `AbstractOverReplicationHandler.selectReplicasToRemove`, and sends throttled delete commands.

Control flow: non-healthy or non-in-service replicas are removed before over-replication evaluation to avoid deleting the only stable copy while stale/dead replicas disappear. If `isOverReplicated()` is false, or if pending deletes already correct the excess, it returns zero. Otherwise it builds a list of pending-delete datanodes, keeps only healthy `CLOSED` replicas not already pending delete, selects candidates, counts candidate replicas by EC index, and deletes a candidate only when its current index count is at least two. After each successful delete, it decrements the local count.

State and persistence: no local persistent state. Delete commands flow through `ReplicationManager.sendThrottledDeleteCommand`, which enforces per-datanode delete limits and records pending delete ops.

Dependencies and integration: it depends on `ReplicationManager` for node health and delete command dispatch, `PlacementPolicy` through the abstract superclass, EC count logic, node status, and container replica state. `ReplicationManager.processOverReplicatedContainer` selects it for EC containers.

Risks: candidate selection requests only one removal (`selectReplicasToRemove(candidates, 1)`) even if multiple indexes are over-replicated, so repeated queue passes may be required. The placement-policy selection is index-agnostic, and the handler relies on the index-count sanity check to prevent data loss. Filtering out non-healthy nodes avoids a common race but can delay cleanup of excess stale records.

Test signals: `TestECOverReplicationHandler` covers pending delete short-circuiting, non-healthy replica filtering, no-delete cases, overloaded delete targets, and preserving at least one copy per EC index.
