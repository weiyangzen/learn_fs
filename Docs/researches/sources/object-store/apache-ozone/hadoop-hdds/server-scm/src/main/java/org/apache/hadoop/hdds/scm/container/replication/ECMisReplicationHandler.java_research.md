# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ECMisReplicationHandler.java

Purpose: `ECMisReplicationHandler` specializes the abstract `MisReplicationHandler` for EC containers. It fixes placement-policy violations only after the common mis-replication flow confirms the container is neither under- nor over-replicated and has no pending operations.

Important APIs and behavior: `getContainerReplicaCount` validates that the container replication type is `EC` and creates an `ECContainerReplicaCount`. `sendReplicateCommands` sends one command per source replica and target datanode, preserving the EC replica index in the command.

Control flow: the inherited flow selects healthy in-service `CLOSED` or `QUASI_CLOSED` source replicas, asks the placement policy which replicas should be copied, computes target datanodes, then calls this class to issue commands. EC command emission walks `replicasToBeReplicated` and `targetDns` together until targets are exhausted. In push mode it calls `ReplicationManager.sendThrottledReplicationCommand(containerInfo, singleton source, target, replicaIndex)`. In pull mode it builds `ReplicateContainerCommand.fromSources`, sets the EC replica index, and sends it to the target.

State and persistence: the handler keeps no state. Command state is recorded by `ReplicationManager.sendDatanodeCommand`, which schedules pending add ops and metrics.

Dependencies and integration: it depends on `PlacementPolicy`, SCM configuration, `ReplicationManager`, EC replica counts, `ReplicateContainerCommand`, and Ratis `NotLeaderException`. It is selected by `ReplicationManager.processUnderReplicatedContainer` when a health result is `MIS_REPLICATED` and replication type is EC.

Risks: the handler ignores the `sources` list passed by the abstract class and uses the datanode of each selected source replica directly, which is correct for per-index EC copies but assumes `replicasToBeReplicated` only contains usable sources. If target count is smaller than source count, it silently stops after available targets and the parent detects partial placement by comparing target count with required count. Overloaded sources are collected and rethrown after the loop so partial progress can occur.

Test signals: `TestECMisReplicationHandler` and `TestMisReplicationHandler` exercise EC type validation, placement target selection, push/pull command construction, replica-index preservation, and partial target handling.
