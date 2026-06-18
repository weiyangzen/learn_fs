<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerStateManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerStateManager.java

## Purpose
Defines the lower-level SCM container state manager contract. It owns container lifecycle state, container table persistence, in-memory replica sets, matching-container selection, and HA-replicated mutation entry points.

## Important APIs, Types, And Functions
Read APIs include `contains`, `getContainerIDs`, `getContainerInfos`, `getContainerCount`, `getContainer`, and `getContainerReplicas`. Replica APIs are `updateContainerReplica` and `removeContainerReplica`. Replicated mutations include `addContainer`, `updateContainerStateWithSequenceId`, `transitionDeletingOrDeletedToTargetState`, `removeContainer`, and `updateContainerInfo`. `updateDeleteTransactionId`, `getMatchingContainer`, and `reinitialize` round out the contract. `getType` identifies the HA request type as `SCMRatisProtocol.RequestType.CONTAINER`.

## Control Flow
The interface documents the lifecycle state machine: OPEN to CLOSING via FINALIZE, CLOSING to QUASI_CLOSED or CLOSED, QUASI_CLOSED to CLOSED, CLOSED or QUASI_CLOSED to DELETING, and DELETING to DELETED. Replicated methods must be idempotent, use protobuf arguments, and be suitable for SCM HA invocation.

## State And Persistence
The state manager is responsible for persistent `ContainerInfo` records and in-memory replica locations. The interface explicitly separates replicated persistent mutations from non-replicated report-derived replica updates.

## Dependencies And Integration Points
Extends `SCMHandler` and depends on `@Replicate`, container lifecycle protobufs, SCM Ratis request types, pipeline IDs, container table storage, and the state-machine exception type. It is the HA-facing backend for `ContainerManagerImpl`.

## Risks And Test Signals
Replicated mutation signatures are constrained by HA requirements; changing them can break Ratis invocation. The bypass transition from DELETING/DELETED back to CLOSED/QUASI_CLOSED is intentionally outside the normal state machine. Tests should cover lifecycle transition validity, idempotent repeated events, HA proxy invocation, table reinitialization, replica operations, and matching-container behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerStateManager.java -->
