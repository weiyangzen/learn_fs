<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerStateManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerStateManagerImpl.java

## Purpose
Default `ContainerStateManager` implementation. It keeps container metadata in an in-memory `ContainerStateMap` backed by the SCM container table and transaction buffer, maintains report-derived replica sets, tracks round-robin container selection, and exposes HA-proxied replicated mutations.

## Important APIs, Types, And Functions
The private constructor initializes locks, state machine, configured container size, `ContainerStateMap`, `lastUsedMap`, transaction buffer, striped per-container locks, and pending-op hooks. `newStateMachine` defines lifecycle transitions and idempotent self-transitions. `initialize` loads all containers from the table and registers OPEN containers with existing pipelines. Mutators include `addContainer`, `updateContainerStateWithSequenceId`, `transitionDeletingOrDeletedToTargetState`, `updateContainerReplica`, `removeContainerReplica`, `updateDeleteTransactionId`, `removeContainer`, `reinitialize`, and `updateContainerInfo`. `getMatchingContainer` implements round-robin space selection.

## Control Flow
Startup iterates the table into memory, warning when OPEN containers reference missing or null pipelines. Adding a container buffers the table write, updates the in-memory map, and registers the container with the pipeline when possible; `ExecutionUtil` rollback removes partial state on failure. State updates synchronize sequence ID from the leader, compute the next lifecycle state, update map indexes, buffer the new table value, and run side effects such as removing finalized containers from pipelines. Matching starts after the last used ID, wraps to the head set, updates last-used time, and records the selected container.

## State And Persistence
Persistent state is `ContainerInfo` in `containerStore`, updated through `DBTransactionBuffer`. In-memory state includes `ContainerStateMap`, replica sets, `lastUsedMap`, and pipeline-container registrations. Replica add/remove completes pending replication/delete operations but does not write the container table. `updateContainerInfo` currently persists only the suppressed flag from the supplied proto onto the existing container.

## Dependencies And Integration Points
Depends on SCM config, `PipelineManager`, `DBTransactionBuffer`, `ContainerReplicaPendingOps`, `ContainerStateMap`, `StateMachine`, `ExecutionUtil`, Guava striped locks, SCM Ratis proxy invocation, and container table iterators. The builder wraps the implementation with `ContainerStateManagerInvoker` from `SCMRatisServer`.

## Risks And Test Signals
The class comment says calls are not thread safe, but the implementation uses global and striped locks; lock coverage and ordering are still important. Some rollback paths buffer or write old values and should be tested under injected failures. Pipeline registration for OPEN containers with missing metadata has special Recon behavior. Tests should cover table load, add rollback, idempotent transitions, sequence ID synchronization, FINALIZE pipeline removal, DELETING/DELETED resurrection bypass, pending-op completion on replica changes, matching-container wraparound, delete transaction persistence, and reinitialize.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerStateManagerImpl.java -->
