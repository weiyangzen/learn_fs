# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/RatisOverReplicationHandler.java

Purpose: `RatisOverReplicationHandler` removes excess Ratis replicas while preserving enough matching replicas, unique origins for non-closed containers, and placement-policy quality.

Important APIs and behavior: `processAndSendCommands` filters replicas to healthy datanodes, builds a `RatisContainerReplicaCount` with unhealthy considered, verifies over-replication, builds eligible delete candidates, computes excess redundancy, and sends delete commands. `getEligibleReplicas` sorts candidates deterministically, removes non-`IN_SERVICE` and pending-delete replicas, and for non-`CLOSED` containers saves one replica per unique origin. `createCommands` deletes mismatched-state replicas before deleting otherwise healthy excess replicas.

Control flow: after mismatched replicas are targeted, the handler removes them from the candidate list and performs placement-aware deletion. It computes original placement status and only deletes a replica if `isPlacementStatusActuallyEqualAfterRemove` says removing it does not worsen placement, or preserves the same placement count when already mis-replicated. Even failed throttled delete attempts for selected replicas decrement local excess to keep deterministic selection and avoid deleting extra healthy replicas later.

State and persistence: no handler persistence. Delete command scheduling and pending ops are handled by `ReplicationManager`. Local `replicaSet` models deletions already selected in the current pass.

Dependencies and integration: depends on `AbstractOverReplicationHandler`, `PlacementPolicy`, `ReplicationManager`, `ReplicationManagerUtil.findNonUniqueDeleteCandidates`, `NodeStatus`, and Ratis count logic. `ReplicationManager.processOverReplicatedContainer` selects it for ordinary Ratis over-replication.

Risks: treating failed mismatched deletes as locally removed is deliberate but can leave actual excess until retry. `allUnhealthy` sorting by sequence ID only applies when healthy count is zero, so mixed unhealthy and healthy cases use hash ordering after mismatched preference. Placement equality checks are central to avoiding a fix that creates mis-replication.

Test signals: `TestRatisOverReplicationHandler` covers healthy filtering, pending deletes, unique-origin preservation, mismatched replica deletion preference, placement-aware deletion, all-unhealthy sorting, and overloaded delete exceptions.
