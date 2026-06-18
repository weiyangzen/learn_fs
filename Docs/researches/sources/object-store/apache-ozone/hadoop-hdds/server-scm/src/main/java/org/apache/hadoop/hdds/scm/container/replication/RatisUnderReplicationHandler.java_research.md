# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/RatisUnderReplicationHandler.java

Purpose: `RatisUnderReplicationHandler` creates additional replicas for under-replicated Ratis containers. It supports normal healthy-source replication, only-unhealthy recovery, vulnerable unhealthy quasi-closed replicas, and target-unblocking by deleting unhealthy replicas when placement cannot find a target.

Important APIs and behavior: `processAndSendCommands` skips empty `QUASI_CLOSED` containers, builds count objects with and without unhealthy replicas, handles `UnderReplicatedHealthResult.hasVulnerableUnhealthy`, verifies real under-replication after pending adds, selects sources, selects placement targets, sends push or pull replication commands, and throws `InsufficientDatanodesException` on partial target results.

Control flow: `verifyUnderReplication` returns null for already sufficient, pending-add sufficient, or unrecoverable containers. It chooses the count excluding unhealthy replicas when any healthy replicas exist, otherwise the count including unhealthy replicas. `getSources` prefers `CLOSED` replicas, allows `QUASI_CLOSED` when no closed replicas exist or the container is quasi-closed, allows `UNHEALTHY` only when no healthy replicas exist, filters to healthy datanodes not pending delete, and keeps only replicas at the maximum sequence ID. Vulnerable unhealthy handling replicates each vulnerable source independently and updates used nodes after success.

State and persistence: local state is per-call only. `sendReplicationCommands` uses `ReplicationManager` to schedule pending adds and metrics. `removeUnhealthyReplicaIfPossible` may send an unthrottled delete command to free a target when placement is blocked.

Dependencies and integration: depends on Ratis placement policy, SCM config, `ReplicationManagerUtil`, `RatisContainerReplicaCount`, `ReplicationManager`, `ReplicateContainerCommand`, and metrics. `ReplicationManager` selects it for ordinary Ratis under-replication.

Risks: max-sequence filtering prevents stale copy propagation but can eliminate otherwise available sources. Vulnerable unhealthy replication shuffles sources, which improves fairness but makes exact command order nondeterministic. Deleting an unhealthy replica to unblock placement must respect pending deletes and unique-origin logic in `ReplicationManagerUtil.selectUnhealthyReplicaForDelete`.

Test signals: `TestRatisUnderReplicationHandler` covers source-state selection, max sequence ID, only-unhealthy recovery, vulnerable unhealthy replicas, pending adds, placement failures, delete-unblock behavior, push/pull command generation, and partial replication metrics.
