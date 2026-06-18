# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestHddsDispatcher.java

## Purpose
`TestHddsDispatcher` validates the datanode container command dispatcher for write/read chunk flows, implicit container creation, checksum validation, token verification, disk-full handling, close-container action generation, and min-free-space enforcement. It acts as an integration-style test around `HddsDispatcher`, `Handler` instances, `ContainerSet`, `MutableVolumeSet`, container metrics, and datanode state context.

## Important APIs, Types, And Functions
- `HddsDispatcher.dispatch`, `setClusterId`, `getContainer`, and `createContainer` are the central production APIs.
- Request helpers create `ContainerCommandRequestProto` messages for `WriteChunk`, `ReadChunk`, `PutSmallFile`, `PutBlock`, `ListBlock`, and `CreateContainer`.
- `createDispatcher` constructs a real `MutableVolumeSet`, formats/starts volumes, builds handlers for every `ContainerType` using `Handler.getHandlerForContainerType`, and optionally installs a `TokenVerifier`.
- Disk-space tests use `HddsVolume`, `MockSpaceUsageSource`, `MockSpaceUsageCheckFactory`, `DatanodeConfiguration` free-space keys, and volume stats counters.
- Heartbeat/action integration uses `StateContext.addContainerActionIfAbsent` and `DatanodeStateMachine.triggerHeartbeat`.

## Control Flow
The dispatcher is usually initialized with temporary datanode and metadata directories, a random SCM ID, and handlers backed by a fresh `ContainerSet`. The normal write path sends `WriteChunk`, verifies success, reads the chunk back, optionally commits it with `PutBlock`, and lists block metadata. One test verifies that a `WriteChunk` can implicitly create a missing container, while commit-stage write without a container returns `CONTAINER_NOT_FOUND`. Failure tests spy on `createContainer` to return `DISK_OUT_OF_SPACE` and assert the dispatcher logs creation failure. Duplicate tests send the same write and put-block requests repeatedly and assert idempotent success and a single block entry. Malformed put-block data returns `MALFORMED_REQUEST` without marking the container unhealthy. Checksum tests enable chunk data validation and verify write/read checksum paths and `PutSmallFile`. Token tests enumerate dispatcher contexts that must skip verification for internal Ratis stages and contexts that must call the verifier.

## State And Persistence Behavior
The tests create real temporary volume directories and container files through `MutableVolumeSet`, `HddsVolume`, and `KeyValueContainer.create`. Container state transitions matter: implicitly created containers remain open, already-existing create requests must not mark containers unhealthy, malformed requests must not poison the container, and near-full containers trigger close actions. Disk-space tests update cached usage with `incrementUsedSpace` so local enforcement reads the same cache used by production code. The dispatcher also updates metrics counters for soft-band and hard-limit write requests.

## Dependencies And Integration Points
This suite integrates container command protobuf builders, `BlockID`, checksum utilities, Ratis `DispatcherContext`, token verification, Ozone configuration, volume choosing policies, `ContainerChecksumTreeManager`, `StateContext`, `ContainerMetrics`, and mocked datanode details. It covers the handoff from command dispatch into type-specific handlers and from disk/full conditions into SCM-facing container actions and heartbeat triggers.

## Risks And Edge Cases
Covered risks include idempotent duplicate writes, implicit creation failure, container-not-found at commit stage, checksum enforcement, malformed block metadata, overfull containers, volume hard free-space rejection, soft free-space telemetry, and accidental token checks during internal state-machine phases. A subtle risk is heartbeat throttling: repeated full-container writes should enqueue actions but not trigger unbounded immediate heartbeats per container.

## Test Signals
The file provides strong integration signals because it uses real volume setup for most paths. Assertions cover response result codes, data round trips, logs, container health flags, action counts, heartbeat counts, token verifier invocation, and volume stats metrics. It does not fully simulate concurrent dispatcher calls or all command types, but it covers high-risk write-path behavior.
