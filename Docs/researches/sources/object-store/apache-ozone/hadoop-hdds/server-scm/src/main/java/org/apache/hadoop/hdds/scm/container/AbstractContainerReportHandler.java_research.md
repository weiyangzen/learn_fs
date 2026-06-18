<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/AbstractContainerReportHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/AbstractContainerReportHandler.java

## Purpose
Provides shared logic for full and incremental container report handlers. It updates SCM's container stats, lifecycle state, and replica map from datanode-reported `ContainerReplicaProto` records, and emits delete-container commands for stale or invalid replicas.

## Important APIs, Types, And Functions
Subclasses supply `getLogger()`. `processContainerReplica` synchronizes on `ContainerInfo`, updates stats, applies lifecycle transitions, and updates/removes the replica record. `getDetailsForLogging` lazily formats container/replica/datanode details. `updateContainerStats` adjusts sequence ID, used bytes, and key count for healthy replicas with RATIS or EC-specific aggregation. `updateContainerState` maps SCM lifecycle states and replica states to state-machine events or delete commands. `deleteReplica` publishes `DeleteContainerCommand` with the current SCM leader term.

## Control Flow
Replica processing first updates stats when the replica is not unhealthy, invalid, or deleted. RATIS stats compare all replicas; open containers take minimum usage while non-open containers take maximum usage. EC stats consider replica index 1 and parity indexes because other data indexes may be smaller. Then lifecycle handling finalizes OPEN containers when a non-OPEN replica appears, closes CLOSING/QUASI_CLOSED containers on matching closed replicas and BCSID, deletes empty replicas for DELETED containers, force-deletes EC deleted/deleting leftovers, and can resurrect DELETING/DELETED RATIS containers to CLOSED or QUASI_CLOSED when a non-empty valid replica is discovered.

## State And Persistence
The class mutates `ContainerInfo` fields in memory and calls `ContainerManager` for state transitions and replica updates. State transitions may be persisted and replicated by `ContainerStateManager`; replica location updates are in-memory SCM state. Delete-container commands are emitted to the event bus rather than persisted here.

## Dependencies And Integration Points
Depends on `NodeManager`, `ContainerManager`, `SCMContext`, SCM events, datanode command wrappers, `DeleteContainerCommand`, container lifecycle enums, EC replication config, container checksums, and Ratis leader-term access. It is the shared bridge from datanode container reports into SCM container metadata, replication-manager observations, and command dispatch.

## Risks And Test Signals
Concurrency relies on synchronizing the mutable `ContainerInfo`, with a comment noting this should eventually be a container lock. BCSID mismatch handling intentionally skips replica updates in some close paths. DELETING/DELETED resurrection and force-delete behavior are subtle and state-machine bypasses must be tested carefully. Test signals include RATIS and EC stats aggregation, OPEN-to-CLOSING, CLOSING-to-CLOSED, QUASI_CLOSED force close, deleted empty replica deletion, EC orphan deletion, BCSID mismatch logging, not-leader skip behavior, and replica add/remove correctness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/AbstractContainerReportHandler.java -->
