# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueHandler.java

## Purpose
`TestKeyValueHandler` is a broad unit/integration test suite for `KeyValueHandler`, the datanode-side handler for key-value container commands. It validates command dispatch, volume layout selection, container lifecycle transitions, deletion cleanup, checksum reconciliation, closed-container recovery writes, ICR emission, and read-block metrics.

## Important APIs, types, and functions
The suite exercises `KeyValueHandler.dispatchRequest`, `handleCreateContainer`, `handleCloseContainer`, `deleteContainer`, `markContainerForClose`, `closeContainer`, `reconcileContainer`, `updateContainerChecksum`, `handleGetContainerChecksumInfo`, `readBlock`, `writeChunkForClosedContainer`, and `putBlockForClosedContainer`. It builds `ContainerCommandRequestProto` messages for `CreateContainer`, `ReadContainer`, `UpdateContainer`, `DeleteContainer`, `CloseContainer`, `PutBlock`, `GetBlock`, `ReadChunk`, `WriteChunk`, `PutSmallFile`, `GetSmallFile`, `FinalizeBlock`, and checksum/read-block commands. Test support types include `ContainerSet`, `MutableVolumeSet`, `HddsVolume`, `KeyValueContainerData`, `KeyValueContainer`, `ContainerChecksumTreeManager`, `ContainerMerkleTreeWriter`, `OnDemandContainerScanner`, and `ContainerMetrics`.

## Control flow
Setup creates a mocked `HddsDispatcher` wired to a mocked `KeyValueHandler`, a mocked `ContainerSet`, and a temporary datanode/metadata directory. Dispatch tests send each command type through `KeyValueHandler.dispatchRequest` and verify the correct handler method or unsupported-operation path. Lifecycle tests create real temporary volumes and containers, then mutate states such as `INVALID`, `RECOVERING`, `OPEN`, `CLOSING`, and `CLOSED` before invoking close/delete paths. Failure tests inject `StorageContainerException`, impossible deleted-container directories, failed volumes, mocked clocks for delete timeouts, and an override that forces unreferenced file deletion to fail.

## State and persistence behavior
The tests assert that create failures release committed bytes, delete removes containers from `ContainerSet`, failed delete moves trigger `checkVolumeAsync`, failed-volume deletes log without normal cleanup, and delete decrements cached volume used space by `containerData.getBytesUsed()`. Checksum tests persist and read container Merkle-tree files, update container data checksums, and verify checksum values are reflected in ICR reports. Closed-container paths persist block data and bytes-used metadata while preserving or updating BCSID according to overwrite flags.

## Dependencies and integration points
The file integrates Ozone container metadata, volume selection, metrics, token-free dispatcher flow, checksum tree management, datanode state context, incremental container reports, and the on-demand scanner registered on `ContainerSet`. It also relies on `ContainerLayoutTestInfo.ContainerTest` to run selected cases across `FILE_PER_BLOCK` and `FILE_PER_CHUNK` layouts.

## Risks and edge cases
Covered risks include dispatching create requests to the wrong datanode or replica, leaking committed space on failed container creation, deleting containers on failed volumes, volume-scan triggering on deletion failures, invalid close transitions, recovering-container scan triggers, stale or missing checksum state, invalid states for checksum info, timeout-sensitive deletes, and bytes-used errors during closed-container recovery writes.

## Test signals
Assertions combine Mockito invocation counts, `ContainerProtos.Result` checks, filesystem existence checks, RocksDB metadata reads, metric counter assertions for `bytesReadBlock`, and checksum-tree comparison helpers. A failure here usually signals a regression in datanode command routing, container lifecycle persistence, checksum reporting, or volume accounting.
