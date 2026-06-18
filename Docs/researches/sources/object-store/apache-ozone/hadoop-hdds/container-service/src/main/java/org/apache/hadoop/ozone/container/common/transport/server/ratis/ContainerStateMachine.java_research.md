<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/ContainerStateMachine.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/ContainerStateMachine.java

## Purpose

`ContainerStateMachine` is the Ratis `StateMachine` implementation that applies replicated Ozone container commands. It separates read-only queries, `WriteChunk` state-machine data writes, and committed metadata/application operations; maintains snapshot state for containers created in a pipeline; and coordinates dispatcher execution with Ratis log ordering. The complete 1360-line file was read.

## Important APIs, Types, and Functions

The class extends `BaseStateMachine`. Important lifecycle methods are `initialize`, `takeSnapshot`, `loadSnapshot`, `persistContainerSet`, `close`, and `notifyGroupRemove`. Ratis data-plane methods include `startTransaction(RaftClientRequest)`, `startTransaction(LogEntryProto, RaftPeerRole)`, `write`, `flush`, `read`, `query`, `stream`, `link`, `applyTransaction`, `notifyTermIndexUpdated`, `truncate`, and leadership/failure notifications. Nested helpers include `TaskQueueMap`, `Context`, and `WriteFutures`.

## Control Flow

Leader `startTransaction` validates the container command, clears encoded tokens before logging, rejects operations against finalized blocks, splits `WriteChunk` payload bytes into state-machine data while logging a metadata-only command, and records pending apply metrics. Follower/log replay `startTransaction` reconstructs the full request by combining log metadata with state-machine data. `write` only handles `WriteChunk`: it optionally caches data on the leader, dispatches the WRITE_DATA stage through a per-block chunk executor, records bytes written, and completes a raft future. `applyTransaction` removes stale cached data, builds an APPLY_TRANSACTION context, acquires a semaphore bounding pending apply work, submits the command to a per-container task queue for ordering, updates last-applied indexes only on healthy success, and marks the state machine unhealthy on serious failures. `query` dispatches read-only commands directly. `read` returns state-machine data from the transaction, leader cache, or disk by dispatching a temporary `ReadChunk` command for slow followers. `stream` and `link` integrate Ratis data stream writes with `KeyValueStreamDataChannel`.

## State and Persistence Behavior

Persistent Ratis state is a snapshot file containing `Container2BCSIDMapProto`, written from `container2BCSIDMap` and loaded at initialization to rebuild missing-container validation. Write chunk bytes are not persisted in the Ratis log entry; they are written directly through the dispatcher and temporarily retained in `stateMachineDataCache` for follower replication. `applyTransactionCompletionMap` tracks contiguous completed log indexes before updating last applied. `unhealthyContainers` and `stateMachineHealthy` stop further writes after serious data or apply failures. `containerTaskQueues` preserves per-container apply order.

## Dependencies and Integration Points

This class is tightly coupled to Apache Ratis state-machine APIs, `XceiverServerRatis`, `ContainerDispatcher`, `ContainerController`, `KeyValueStreamDataChannel`, HDDS/Ozone protobuf command types, `ResourceCache`, `TaskQueue`, and `CSMMetrics`. It calls back to `XceiverServerRatis` for follower slowness, no-leader, apply failure, log failure, snapshot-install, group add/remove, and leader-change events.

## Risks and Edge Cases

The state machine intentionally becomes unhealthy on most write/apply/read-state-machine failures, leading to pipeline close or server division close. Some container results (`CONTAINER_NOT_OPEN`, `CLOSED_CONTAINER_IO`, `CHUNK_FILE_INCONSISTENCY`) are tolerated. Long-running write detection cancels all pending write chunks for the group. The snapshot contains metadata for validation but cannot be used for follower catch-up, so install-snapshot notifications trigger pipeline close. Cache eviction policy and `waitOnBothFollowers` affect whether slow followers can read data from cache or must read from disk. `notifyLogFailed` calls `TermIndex.valueOf(failedEntry)` even when `failedEntry` may be null, which deserves defensive test coverage.

## Test Signals

Tests should cover WriteChunk data/log splitting, token clearing, finalized-block rejection, per-container apply ordering, semaphore release on success and failure, tolerated versus fatal result handling, snapshot write/load and missing-container validation, cache hit/miss/disk-read follower paths, long-running write cancellation, `flush` waiting on prior write futures, leader stepdown cache eviction, group removal quasi-close behavior, and callbacks that trigger pipeline-close actions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/ContainerStateMachine.java -->
