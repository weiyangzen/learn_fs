# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestRatisContainerReplicaCount.java

Purpose: Tests `RatisContainerReplicaCount`, the health/counting model for Ratis containers. It evaluates sufficient replication, over-replication, unrecoverability, pending add/delete effects, decommission/maintenance treatment, unhealthy/mismatched replica accounting, remaining redundancy, and quasi-closed sequence correctness.

Important APIs and types: Uses `RatisContainerReplicaCount`, `RatisReplicationConfig`, `ContainerInfo`, `ContainerReplica`, `ContainerReplicaOp`, `ContainerID`, node op states, replica states (`CLOSED`, `CLOSING`, `OPEN`, `QUASI_CLOSED`, `UNHEALTHY`), and helper factories from `ReplicationTestUtil`.

Control flow: The tests progress from basic healthy replica counts for replication factor three and one, through pending add/delete combinations, over-replication, and then decommission and maintenance cases. The helper `validate` checks `isSufficientlyReplicated`, `additionalReplicaNeeded`, `isOverReplicated`, and `insufficientDueToOutOfService`. Later tests inspect detailed counters for healthy, matching, mismatched, unhealthy, decommission counts; compare behavior with `considerUnhealthy` true/false; verify safe over-replication requirements; check remaining redundancy; compare sufficient replication with and without pending ops; and validate quasi-closed replicas by sequence ID.

State and persistence behavior: Pure value-object tests. The state is the constructed set of replicas, pending ops, replication factor, min healthy for maintenance, and `considerUnhealthy` mode. No persistence or external manager is involved.

Dependencies and integration points: This counting class feeds Ratis health results and repair handlers, so these tests anchor decisions for under-replication, over-replication, maintenance safety, and whether unhealthy replicas should be counted as excess or unavailable.

Risks and test signals: Risks include counting pending ops too optimistically, mistaking maintenance/decommission replicas for healthy capacity, treating mismatched states as matching, over-deleting when only unhealthy/mismatched replicas are excess, and accepting quasi-closed replicas with stale sequence IDs. Signals are direct assertions on health booleans, deltas, counts, redundancy, and sequence-ID handling.
