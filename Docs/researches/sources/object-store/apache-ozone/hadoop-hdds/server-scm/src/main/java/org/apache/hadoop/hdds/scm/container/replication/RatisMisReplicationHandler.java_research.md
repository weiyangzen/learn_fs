# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/RatisMisReplicationHandler.java

Purpose: `RatisMisReplicationHandler` is the Ratis-specific subclass of `MisReplicationHandler`. It fixes placement-policy violations for Ratis containers by copying the container to selected target datanodes.

Important APIs and behavior: `getContainerReplicaCount` validates the replication type is `RATIS` and returns a `RatisContainerReplicaCount` with `considerUnhealthy=true`. `sendReplicateCommands` sends one command to each selected target, using all available source datanodes for Ratis replication.

Control flow: inherited logic verifies no pending ops, not under-replicated, not over-replicated, and placement violation before target selection. In push mode, the handler sends throttled replication commands to source datanodes with target and replica index `0`. In pull mode, it sends `ReplicateContainerCommand.fromSources(containerID, sources)` to each target.

State and persistence: no local mutable or persistent state. Pending add ops and metrics are created by `ReplicationManager` when commands are sent.

Dependencies and integration: it depends on `PlacementPolicy`, SCM configuration, `ReplicationManager`, `RatisContainerReplicaCount`, `ReplicateContainerCommand`, and `NotLeaderException`. It is selected by `ReplicationManager.processUnderReplicatedContainer` for Ratis `MIS_REPLICATED` health results.

Risks: because `considerUnhealthy=true`, the count check may treat unhealthy replicas as part of the availability model for mis-replication gating. That is consistent with existing Ratis mis-replication behavior but should be reviewed if unhealthy placement repair semantics change. Push mode can throw if all sources are overloaded; unlike EC, Ratis does not collect multiple exceptions because it sends per target.

Test signals: `TestRatisMisReplicationHandler` and `TestMisReplicationHandler` verify type validation, no-op conditions, placement target count, push/pull command construction, and partial target exception behavior.
