# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestContainerBalancerSelectionCriteria.java

## Purpose
`TestContainerBalancerSelectionCriteria` unit-tests `ContainerBalancerSelectionCriteria.shouldBeExcluded`. It verifies that the balancer rejects unhealthy or actively changing containers by default while optionally allowing selected non-standard but safe cases such as over-replicated closed containers and healthy quasi-closed containers.

## Important APIs, Types, and Functions
The fixture uses `ContainerBalancerConfiguration`, `ContainerBalancerSelectionCriteria`, `ContainerManager`, `ReplicationManager`, `NodeManager`, `FindSourceStrategy`, `ContainerHealthResult`, `ReplicationTestUtil`, `ContainerInfo`, and `ContainerReplica`. It constructs RATIS replication with factor THREE and manipulates replica states `CLOSED` and `QUASI_CLOSED`, including an explicit empty quasi-closed replica.

## Control Flow and State Behavior
`setup()` creates a CLOSED container with one CLOSED source replica, mocks container/replica lookup, returns healthy replication status, disables active replication/deletion, and allows source size to leave. Basic tests assert under-replicated, over-replicated, and mis-replicated health results are excluded, while a healthy container is not. When `isContainerReplicatingOrDeleting` is true, the container is excluded after health and replica lookups.

The non-standard container tests pivot on `balancerConfiguration.setIncludeNonStandardContainers`. With the flag enabled, an over-replicated CLOSED container with at least the required number of non-empty CLOSED replicas plus one non-empty QUASI_CLOSED replica can be selected from any replica source. With the flag disabled, the same over-replicated container is excluded. If an over-replicated container has only two CLOSED replicas for RF=3, all sources are excluded because moving any closed or quasi-closed replica could drop below minimum closed coverage. Empty QUASI_CLOSED replicas remain excluded even when non-standard inclusion is enabled. Healthy QUASI_CLOSED containers with all non-empty quasi-closed replicas are allowed only when the flag is enabled.

## Dependencies and Integration Points
This test isolates criteria logic from full balancer execution while using production health-result classes. It is an integration point between replication health classification, source-size checks, replica state/emptiness rules, and the balancer configuration flag for non-standard containers.

## Risks and Test Signals
The main risks are moving containers that replication manager is already repairing, worsening under/over/mis-replication, moving empty quasi-closed replicas, or excluding safe non-standard cases when the operator enables them. Signals are direct boolean assertions on `shouldBeExcluded` and Mockito verifications for expected health checks.
