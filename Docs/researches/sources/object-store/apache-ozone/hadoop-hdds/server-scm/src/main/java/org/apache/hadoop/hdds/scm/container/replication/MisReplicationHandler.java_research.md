# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/MisReplicationHandler.java

Purpose: `MisReplicationHandler` is the shared template for fixing placement-policy violations when a container is otherwise sufficiently replicated and not over-replicated. It is subclassed by Ratis and EC handlers for replica-count construction and command emission.

Important APIs and behavior: subclasses implement `getContainerReplicaCount` and `sendReplicateCommands`. The main `processAndSendCommands` rejects containers with pending ops, verifies sufficient and not over-replicated state, validates current placement, selects eligible source replicas, asks the placement policy which replicas should be copied, computes target datanodes, dispatches subclass commands, and throws `InsufficientDatanodesException` if placement found fewer targets than required.

Control flow: `filterSources` allows `CLOSED` and `QUASI_CLOSED` replicas on healthy `IN_SERVICE` datanodes. The placement policy receives a map of every replica to a boolean indicating source eligibility via `replicasToCopyToFixMisreplication`. Used/excluded nodes are computed by `ReplicationManagerUtil`, with selected source replicas excluded so new copies do not land on inappropriate hosts. Partial placement increments EC or Ratis mis-replication metrics.

State and persistence: the handler stores injected placement policy, current container size, `ReplicationManager`, and metrics. It does not persist decisions; commands sent through `ReplicationManager` create pending add records and metrics.

Dependencies and integration: it integrates placement policy, SCM config, `ReplicationManagerUtil`, node health lookup, and per-type subclasses. `ReplicationManager.processUnderReplicatedContainer` uses it for `MIS_REPLICATED` health results.

Risks: skipping all mis-replication work when any pending op exists is conservative but can delay placement repair behind unrelated delete/add work. If placement policy marks a replica for copying that is no longer in `filterSources`, subclass command logic must tolerate missing or unusable sources. The raw `new ArrayList(replicas)` call loses generic type information but is not behaviorally significant.

Test signals: `TestMisReplicationHandler`, `TestRatisMisReplicationHandler`, and `TestECMisReplicationHandler` cover pending-op suppression, placement-satisfied no-op, insufficient target metrics, and type-specific command behavior.
