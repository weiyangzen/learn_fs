# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestContainerPlacementStatusDefault.java

Purpose: This compact suite locks down how `ContainerPlacementStatusDefault` reports policy satisfaction and misreplication counts for rack-placement results.

Important APIs and types: It constructs `ContainerPlacementStatusDefault` with actual placement count, expected placement count, total rack count, and in some cases per-rack occupancy inputs. It asserts `isPolicySatisfied` and `misReplicationCount`.

Control flow: `testPlacementSatisfiedCorrectly` covers cases where actual placement meets expected placement or where the cluster cannot provide enough racks, so the effective policy is satisfied. `testPlacementNotSatisfied` covers insufficient rack spread and occupancy constraints, including zero actual racks and cases where multiple additional rack placements are needed.

State and persistence behavior: There is no persistence. State is immutable placement-count data passed into the status object.

Dependencies and integration points: The status object is returned by placement policies and consumed by replication manager health checks, misreplication repair, and over/under placement diagnostics.

Risks: The tests encode exact misreplication arithmetic. If policy semantics change, especially for clusters with fewer racks than requested or per-rack replica constraints, these assertions must be updated intentionally.

Test signals: Exact boolean satisfaction results and exact `misReplicationCount` values, including satisfied single-rack cluster cases and unsatisfied multi-rack / per-rack occupancy cases.
