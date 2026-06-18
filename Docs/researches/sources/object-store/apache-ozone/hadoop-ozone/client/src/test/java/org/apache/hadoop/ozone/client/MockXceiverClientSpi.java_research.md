# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MockXceiverClientSpi.java

## Purpose
`MockXceiverClientSpi` is the mocked datanode RPC client used by unit tests. It translates container command protobuf requests into operations on a single `MockDatanodeStorage`.

## Important APIs, Types, And Functions
`sendCommandAsync` supports `WriteChunk`, `ReadChunk`, `PutBlock`, `GetBlock`, and `ListBlock`. Helper methods build response protobufs and wrap them in completed `XceiverClientReply` futures. `writeChunk` writes chunk bytes and optionally processes the embedded block data. `doPutBlock` computes committed block length, stores block metadata, and returns `GetCommittedBlockLengthResponseProto`.

## Control Flow
Each command type maps directly to storage operations. `WriteChunk` catches `ContainerNotOpenException` as `CLOSED_CONTAINER_IO` and other `IOException`s as `IO_EXCEPTION`; other command paths assume success unless storage assertions fail. `result` initializes a successful response and lets helpers add command-specific payloads.

## State And Persistence Behavior
The SPI itself holds immutable references to a `Pipeline` and `MockDatanodeStorage`. Persistent test data lives in the storage object. `connect`, `close`, release, replicated min commit index, and all-node command semantics are effectively no-ops or placeholders.

## Dependencies And Integration Points
It extends `XceiverClientSpi` and consumes HDDS datanode container protobufs. It is produced by `MockXceiverClientFactory` and exercised by `KeyOutputStream`, `ECKeyOutputStream`, `KeyInputStream`, and checksum helper code.

## Risks And Edge Cases
Only a subset of datanode commands is implemented. `sendCommandOnAllNodes` returns null, so tests requiring replicated fanout semantics cannot rely on it. Error handling is limited mostly to write chunk. It does not model network latency, asynchronous failures, leader/follower behavior, or commit index advancement.

## Test Signals
All in-memory key IO tests depend on this class. EC tests validate the behavior through actual write/read paths, while checksum tests use mocked or real xceiver responses to verify checksum computation.
