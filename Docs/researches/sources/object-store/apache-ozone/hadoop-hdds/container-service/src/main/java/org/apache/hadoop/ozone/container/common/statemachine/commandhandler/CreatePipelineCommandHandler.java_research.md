# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/CreatePipelineCommandHandler.java

## Purpose
Handles SCM create-pipeline commands by creating a local write-channel group and propagating Ratis group creation to peer datanodes.

## Important APIs and Types
Implements `CommandHandler` for `createPipelineCommand`. It uses injected Ratis client factory and executor, per-pipeline in-progress deduplication, queue/invocation counts, and latency metrics.

## Control Flow
`handle()` casts the command, deduplicates by pipeline UUID, schedules async work, checks if the local write channel already has the pipeline, constructs a `RaftGroup` from peer datanodes and priorities, calls `server.addGroup()`, then sends group-management `add()` to peer Raft servers except itself. `AlreadyExistsException` is benign.

## State and Persistence Behavior
Persistent state changes happen in the write channel/Ratis group storage. The handler maintains only in-memory queue count, invocation count, metrics, and in-progress UUID set.

## Dependencies and Integration Points
It uses `OzoneContainer.getWriteChannel()`, `RatisHelper`, `RaftClient`, peer `DatanodeDetails`, TLS config, and `PipelineID`.

## Risks
Peer group creation is best-effort: IO failures are warnings after local add may have succeeded. The in-progress marker must be cleared on all completion and rejection paths. Existing local groups cause a silent no-op, which is idempotent but can hide partial peer propagation.

## Test Signals
Tests should verify local add, peer propagation, duplicate suppression, already-exists handling, rejection cleanup, queue count decrement, and behavior when the pipeline already exists.
