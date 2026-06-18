# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineManagerImpl.java

## Purpose
`PipelineManagerImpl` is the HA-aware implementation of `PipelineManager`. It coordinates pipeline creation, state transitions, DB-backed state manager operations, background creation/scrubbing services, container close events, node reverse indexes, pending allocation checks, JMX, and metrics.

## Important APIs, Types, And Functions
`newPipelineManager` constructs `PipelineStateManagerImpl`, `PipelineFactory`, `BackgroundPipelineCreator`, and a periodic scrubber service, then freezes or resumes pipeline creation based on finalization checkpoint. Creation flows include `buildECPipeline`, `addEcPipeline`, `createPipeline`, `addPipelineToManager`, and explicit-node/read creation. Lifecycle flows include `openPipeline`, `closePipeline`, `deletePipeline`, `removePipeline`, `activatePipeline`, `deactivatePipeline`, `waitPipelineReady`, `waitOnePipelineReady`, and `scrubPipelines`.

Container membership and allocation APIs delegate to state manager and node manager: `addContainerToPipeline`, `removeContainerFromPipeline`, `getContainersInPipeline`, `checkSpaceAndRecordAllocation`, and `openContainerLimit`. Administrative APIs include `closeStalePipelines`, `getStalePipelines`, `sameIdDifferentHostOrAddress`, `freezePipelineCreation`, `resumePipelineCreation`, `isPipelineCreationAllowed`, `reinitialize`, and `close`.

## Control Flow
Pipeline creation first checks whether SCM is leader and safemode prechecks are complete, unless the replication factor is one, and then checks the freeze flag. It creates via `PipelineFactory`, adds through `PipelineStateManager`, and records metrics. Opening an allocated pipeline updates state to OPEN, measures latency, increments created metrics, and creates per-pipeline metrics. Closing first finalizes/open-closes all open containers in the pipeline and fires `CLOSE_CONTAINER` events, then updates pipeline state to CLOSED and removes per-pipeline metrics. Deletion removes pipeline state, updates node reverse indexes, delegates provider close behavior, and updates destroy metrics.

Scrubbing scans all pipelines. ALLOCATED pipelines older than configured timeout are closed and deleted. CLOSED pipelines older than destroy timeout are deleted. OPEN pipelines with unregistered nodes are closed, especially important for EC pipelines after SCM restart. Stale address handling finds pipelines containing the same datanode ID with a different host/IP, closes them, then deletes them.

`waitOnePipelineReady` polls candidate IDs until any pipeline is OPEN or timeout elapses, throwing if none are found or if no candidate opens in time. Pending allocation checks fetch all datanode infos for a pipeline, call node manager reservation per datanode, and rollback successful reservations if any later datanode fails.

## State And Persistence Behavior
The manager owns a `ReentrantReadWriteLock`, provider/state manager references, background service references, metrics source, MBean registration, freeze flag, SCM context, and clock. Durable pipeline state is delegated to `PipelineStateManager`, which replicates and buffers DB changes. Container close events and provider close commands are side effects outside the manager's own state. Creation freeze is in memory and reset by service initialization/finalization logic.

## Dependencies And Integration Points
It depends on SCM HA manager, DB tables, event publisher, SCM service manager, `NodeManager`, `ContainerManager`, `FinalizationManager`, `SCMContext`, `PipelineFactory`, `PipelineStateManager`, `BackgroundSCMService`, `SCMPipelineMetrics`, and Ratis utilities. It registers as `SCMPipelineManagerInfo` MBean and exposes pipeline state counts through `PipelineManagerMXBean`.

## Risks And Edge Cases
Creation checks are split between `isPipelineCreationAllowed`, factor-one bypass, and freeze state; changes to safemode/finalization behavior can accidentally permit or block pipelines. `closePipeline` closes containers before checking if the pipeline is already closed, so repeated calls can still touch containers/events. Scrubber log duration uses `Duration.between(currentTime, creationTimestamp)`, which produces negative durations when creation is before current time. Polling waits use sleep and ignore interruption except setting the interrupt flag, then continue timeout logic.

The state manager can swallow missing-pipeline removals as warnings, so callers may believe deletion succeeded. `checkSpaceAndRecordAllocation` must rollback exactly the successful prefix to avoid pending allocation leaks. Background services must be stopped before unregistering metrics/state manager close to avoid operations against closed stores.

## Test Signals
Tests should cover creation allowed/blocked in leader, follower, safemode, precheck, factor-one, and frozen states; EC build/add validation; metrics increments on allocate/open/destroy/failures; container finalization and close events on pipeline close; scrubber handling for old allocated/closed/open-with-unregistered-node pipelines; stale IP/hostname detection; wait timeout and found/not-found behavior; pending allocation rollback; reinitialize from store; MBean/metrics cleanup on close.
