<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerManager.java

## Purpose
Defines the SCM container management contract: container allocation, lookup, lifecycle changes, replica tracking, delete transaction updates, matching-container selection for writes, report metrics notification, deletion, reinitialization, and metadata updates.

## Important APIs, Types, And Functions
Key APIs include `reinitialize`, `getContainer`, `getContainers`, `getContainerIDs`, `getContainerStateCount`, `getTotalContainerCount`, `containerExist`, `allocateContainer`, `updateContainerState`, `transitionDeletingOrDeletedToTargetState`, `getContainerReplicas`, `updateContainerReplica`, `removeContainerReplica`, `updateDeleteTransactionId`, `getMatchingContainer`, `notifyContainerReportProcessing`, `deleteContainer`, `getContainerStateManager`, and `updateContainerInfo`.

## Control Flow
The interface separates read/list paths, lifecycle mutation paths, replica mutation paths, allocation paths, and report accounting. Default methods provide all-container listing, total count aggregation over lifecycle states, and a simplified `getMatchingContainer` overload without exclusions.

## State And Persistence
Implementations manage persistent `ContainerInfo` records and in-memory replica state. The interface exposes persistent state transitions and metadata updates, but replica locations are typically report-derived and may not be persisted in the same table.

## Dependencies And Integration Points
Depends on `ReplicationConfig`, `Pipeline`, container lifecycle protobuf enums, `ContainerInfoProto`, and the container table abstraction. It is consumed by SCM protocol handlers, report handlers, replication manager, balancer, block allocation, Recon sync paths, and tests.

## Risks And Test Signals
The contract mixes persisted container state and volatile replica state, so callers must know which changes survive restart. `transitionDeletingOrDeletedToTargetState` explicitly bypasses the normal state machine and needs constrained use. Tests should cover allocation, state transitions, replica update/remove, delete transaction updates, matching-container selection, total count, reinitialization, and report-processing metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerManager.java -->
