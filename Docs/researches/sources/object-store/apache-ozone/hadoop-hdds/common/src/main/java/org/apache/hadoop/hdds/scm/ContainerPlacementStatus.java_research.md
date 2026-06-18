# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ContainerPlacementStatus.java

## Purpose
Defines the contract used to report whether a container's replicas satisfy placement policy, independent of under- or over-replication.

## Important APIs, Types, And Functions
The interface declares `isPolicySatisfied()`, `misReplicatedReason()`, `misReplicationCount()`, `expectedPlacementCount()`, and `actualPlacementCount()`.

## Control Flow
Implementations compute rack/node-group or topology placement state. Callers inspect satisfaction first, then use reason/count fields for replication manager decisions and diagnostics.

## State And Persistence
The interface stores no state. Implementations normally derive transient state from replica locations and topology.

## Dependencies And Integration Points
It integrates with SCM placement policies and replication-manager health checks that mark containers as mis-replicated.

## Risks And Test Signals
The interface does not define nullability or exact semantics for count when placement and replication both fail. Tests should cover placement-satisfied, mis-replicated, and under-replicated-but-placement-valid cases.
