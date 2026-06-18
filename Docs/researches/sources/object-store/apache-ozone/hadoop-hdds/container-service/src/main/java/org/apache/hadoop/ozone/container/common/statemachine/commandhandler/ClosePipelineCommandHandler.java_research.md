# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/ClosePipelineCommandHandler.java

## Purpose
Handles SCM close-pipeline commands by removing Ratis or write-channel pipeline groups locally and, for Ratis, requesting peer datanodes to remove the Raft group.

## Important APIs and Types
Implements `CommandHandler` for `closePipelineCommand`. It uses an injected `Executor`, a `BiFunction<RaftPeer, GrpcTlsConfig, RaftClient>`, `MutableRate`, and a concurrent `pipelinesInProgress` set. `isPipelineCloseInProgress(UUID)` is used by `StateContext` to expose in-progress pipeline closes.

## Control Flow
`handle()` deduplicates by pipeline UUID. It schedules async work, fetches the write channel, checks if the pipeline exists, and for `XceiverServerRatis` collects peers and sends group-management `remove()` calls to peers before removing the local group. `GroupMismatchException` is treated as benign because another datanode may have closed the group already. Completion decrements queue count and clears the in-progress marker.

## State and Persistence Behavior
Persistent effects are in the write-channel/Ratis group storage and optional Ratis log directory deletion. Handler state is in-memory deduplication and metrics.

## Dependencies and Integration Points
It integrates with `XceiverServerSpi`, `XceiverServerRatis`, Ratis `RaftClient`, `RatisHelper`, TLS config from `OzoneContainer`, and command queue metrics.

## Risks
Peer remove calls happen best-effort; IO failures are logged but local remove still proceeds. The queue count is manually adjusted and must stay balanced on rejection and completion. In-progress deduplication prevents duplicate work but also means a stuck task suppresses later commands for that pipeline until completion.

## Test Signals
Tests should cover duplicate suppression, Ratis peer removal, local `removeGroup`, benign group-mismatch handling, rejection cleanup, queue count accuracy, and `isPipelineCloseInProgress()`.
