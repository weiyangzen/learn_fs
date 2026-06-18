# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineManager.java

## Purpose
`PipelineManager` is the public SCM interface for pipeline lifecycle, lookup, container membership, background creation control, space-reservation checks, and pipeline metrics.

## Important APIs, Types, And Functions
Creation APIs include `createPipeline`, `buildECPipeline`, `addEcPipeline`, explicit-node creation, and `createPipelineForRead`. Lifecycle APIs include `openPipeline`, `closePipeline`, `deletePipeline`, `activatePipeline`, `deactivatePipeline`, `closeStalePipelines`, and `scrubPipelines`. Query APIs include `getPipeline`, `containsPipeline`, `getPipelines`, `getPipelineCount`, container membership getters, and `getSafeModeStatus`. Operational APIs include creator start/trigger, freeze/resume, HA reinitialization, read/write lock exposure, pending allocation check, open-container limit, and metrics retrieval.

## Control Flow
This is an interface, but it defines expected lifecycle sequencing: pipelines are created/added, opened after reports, closed before deletion, scrubbed when stale in allocated/closed states, and reinitialized from the pipeline store during SCM reload. Default `waitPipelineReady` and `waitOnePipelineReady` are no-ops/null unless implementations override them.

## State And Persistence Behavior
The interface does not own state. Implementations are expected to coordinate in-memory pipeline maps, node reverse indexes, and durable pipeline stores. `reinitialize` explicitly reloads from `Table<PipelineID, Pipeline>`.

## Dependencies And Integration Points
It extends `Closeable` and `PipelineManagerMXBean`. It integrates with SCM container manager through container membership methods, node manager through placement and allocation checks, HA DB table reload, and metrics through `SCMPipelineMetrics`.

## Risks And Edge Cases
Default wait methods can hide missing implementation if a caller uses an implementation that does not override them. Exposing locks in the interface can couple callers to implementation locking and risks deadlocks if misused. Some methods throw checked exceptions while others silently return booleans or nulls in implementations, so callers must follow concrete semantics.

## Test Signals
Contract tests should cover lifecycle ordering, persistence after reinitialize, lock behavior where exposed, allocation rollback, freeze/resume behavior, and wait method behavior for the concrete implementation.
