# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/AbstractOverReplicationHandler.java

Purpose: shared base for over-replication handlers, centralizing placement-aware replica removal helpers.

Important APIs: constructor, `isPlacementStatusActuallyEqualAfterRemove`, `selectReplicasToRemove`, and `getPlacementStatus`.

Control flow and state: holds a `PlacementPolicy`. To test a removal, it temporarily removes a replica from the passed set, computes new placement, then adds the replica back. It considers placement "actually equal" if both statuses are satisfied or if both are unsatisfied with the same actual placement count.

Dependencies and integration: used by concrete Ratis/EC over-replication handlers; delegates removal selection and placement validation to `PlacementPolicy`. Tested through over-replication handler suites.

Risks: mutates the caller's replica set temporarily, which is unsafe if the set is concurrently shared or if exceptions occur between remove/add. Equality ignores detailed max-replica-per-rack violations. Tests should cover placement-preserving deletion and exception-safe behavior expectations.
