# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/ContainerPlacementStatusDefault.java

Purpose: default `ContainerPlacementStatus` implementation for rack-count and max-replicas-per-rack validation.

Important APIs: constructors, `isPolicySatisfied`, `misReplicatedReason`, `misReplicationCount`, `expectedPlacementCount`, and `actualPlacementCount`.

Control flow and state: immutable fields describe required/current/total racks, max replicas per rack, and per-rack replica counts. Policy is satisfied when current racks meet `min(totalRacks, requiredRacks)` and no rack exceeds max replicas.

Dependencies and integration: returned by placement policies and used throughout replication health checks to classify mis-replication. Unit-tested by `TestContainerPlacementStatusDefault` and used in many replication handler tests.

Risks: constructor trusts the caller to provide a rack count list consistent with current racks. Mis-replication count returns the max of missing racks and excess-per-rack sum, which is a policy choice that tests should pin down for mixed violations.
