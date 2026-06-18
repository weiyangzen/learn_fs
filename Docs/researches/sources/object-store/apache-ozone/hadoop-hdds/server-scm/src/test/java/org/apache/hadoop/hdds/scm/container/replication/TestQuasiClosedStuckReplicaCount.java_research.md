# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestQuasiClosedStuckReplicaCount.java

Purpose: Tests `QuasiClosedStuckReplicaCount`, the origin-aware counting model behind quasi-closed stuck replication. It determines whether each origin group is under- or over-replicated using best-origin and other-origin copy targets, with special handling for out-of-service and maintenance replicas.

Important APIs and types: Uses `QuasiClosedStuckReplicaCount`, nested `MisReplicatedOrigin`, `ContainerReplica`, `ContainerID`, `DatanodeID`, node op states, and `QUASI_CLOSED` replica state. `ReplicationTestUtil` creates origin-specific replicas and BCSID variants.

Control flow: The tests build replica sets grouped by origin with different sequence IDs. Correct-replication cases prove best origin target 3 and other-origin target 2 are sufficient for one, two, or three origins. Under-replication cases validate deltas for one or multiple deficient origins. Over-replication cases validate excess deltas for best and other origins. Decommissioning and maintenance cases show out-of-service copies reduce effective availability for under-replication but should not create false over-replication. The shift test introduces a new origin with a higher BCSID and proves the previous best origin can become over-replicated while the new best becomes under-replicated.

State and persistence behavior: Pure in-memory counting. Inputs are replica sets with origin IDs, op states, and sequence IDs; outputs are booleans and `MisReplicatedOrigin` collections with sources and deltas. No external state is read or written.

Dependencies and integration points: This is the core state model consumed by quasi-closed stuck under/over handlers. Its output determines how many replicate or delete commands handlers send per origin.

Risks and test signals: Risks are off-by-one copy targets, treating decommissioned or maintenance replicas as excess, selecting the wrong best origin after higher BCSID appears, and losing source-origin identity. Signals are explicit `isUnderReplicated`, `isOverReplicated`, source counts, replica deltas, and origin-ID assertions.
