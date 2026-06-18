<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/CloseContainerEventHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/CloseContainerEventHandler.java

## Purpose
Handles `CLOSE_CONTAINER` events in SCM. It finalizes open containers, builds close-container commands, optionally delays dispatch through a lease, and sends close commands to the datanodes that host the container.

## Important APIs, Types, And Functions
`CloseContainerEventHandler` implements `EventHandler<ContainerID>`. Constructor dependencies are `PipelineManager`, `ContainerManager`, `SCMContext`, optional `LeaseManager<Object>`, and lease timeout. `onMessage` is the main handler. `triggerCloseCallback` publishes `CommandForDatanode<CloseContainerCommand>`. `getContainerToken` pulls an encoded container token from `StorageContainerManager` when available. `getNodes` uses the container pipeline and falls back to current replicas if the pipeline is missing.

## Control Flow
The handler first requires leader SCM. For an OPEN container, it sends `LifeCycleEvent.FINALIZE` to move it to CLOSING. It reloads `ContainerInfo`, and if the state is CLOSING, creates a `CloseContainerCommand` with force enabled for non-RATIS replication, sets leader term and token, then either acquires a lease for delayed callback or publishes immediately when running without a lease manager, such as in Recon tests. Non-CLOSING containers are logged and ignored.

## State And Persistence
The container state transition is persisted through `ContainerManager.updateContainerState`. The lease manager may keep an in-memory scheduled command until timeout. Commands are emitted to the event bus and later queued to datanodes outside this class.

## Dependencies And Integration Points
Integrates with pipeline lookup, container replica lookup, SCM leader context, lease scheduling, container token generation, close-container datanode command protocol, and the SCM event bus.

## Risks And Test Signals
Correctness depends on leader-term access, token generation, and reliable fallback when the original pipeline has been removed. Lease de-duplication may suppress duplicate close events. Tests should cover leader and non-leader behavior, OPEN finalization, CLOSING command emission, lease callback path, missing pipeline fallback to replicas, non-RATIS force flag, token behavior under `StorageContainerManager`, and invalid state handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/CloseContainerEventHandler.java -->
