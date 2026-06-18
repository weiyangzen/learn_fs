# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueHandlerWithUnhealthyContainer.java

## Purpose
This suite verifies `KeyValueHandler` behavior when containers are unhealthy or when requests target a mismatched EC replica index. It establishes which operations remain readable, which fail with container-state errors, and how marking a container unhealthy behaves on failed versus healthy volumes.

## Important APIs, types, and functions
The tests call `handleReadContainer`, `handleGetBlock`, `handleGetCommittedBlockLength`, `handleReadChunk`, `handleFinalizeBlock`, `handleGetSmallFile`, generic `handle` with a `PutBlock` request, and `markContainerUnhealthy`. Helpers construct dummy handlers with mocked `ContainerSet`, `MutableVolumeSet`, `ContainerMetrics`, `IncrementalReportSender`, `DatanodeStateMachine`, and `ContainerChecksumTreeManager`. Container data is mocked to expose states, BCSID, replica indexes, and container protobuf metadata.

## Control flow
Each operation is invoked directly against a `KeyValueContainer` backed by mocked `KeyValueContainerData`. Unhealthy containers allow `ReadContainer` to return `SUCCESS`, while block/chunk/small-file reads generally fall through to `UNKNOWN_BCSID` due to missing block metadata. `FinalizeBlock` is expected to return `CONTAINER_UNHEALTHY`. Parameterized tests iterate every `ClientVersion` and replica IDs 0 through 5 to verify requests with nonzero replica IDs fail with `CONTAINER_NOT_FOUND` when they mismatch the container replica index.

## State and persistence behavior
The unhealthy mark test builds a real `KeyValueContainerData` with metadata path, DB file, and `HddsVolume`. When the volume state is `FAILED`, `markContainerUnhealthy` must not create the checksum file and must not send an ICR. When the same volume is switched to `NORMAL`, the checksum sidecar file is expected to exist and the ICR sender is invoked at most once.

## Dependencies and integration points
The suite sits at the boundary between request handling, EC replica-index routing, checksum tree sidecar creation, storage-volume state, and incremental container reports. It also uses `ContainerTestHelper` request builders and `MockPipeline` to create a malformed `PutBlock` path that previously risked an NPE.

## Risks and edge cases
Key risks are accidentally rejecting safe read-container requests, returning the wrong error code for unhealthy states, treating replica ID 0 as a strict mismatch, creating checksum files on failed volumes, sending ICRs for containers that cannot be safely persisted, and internal errors from incomplete container mocks.

## Test signals
The strongest signals are exact `ContainerProtos.Result` assertions, file existence checks for `ContainerChecksumTreeManager.getContainerChecksumFile`, and Mockito `never`/`atMostOnce` checks for ICR sends.
