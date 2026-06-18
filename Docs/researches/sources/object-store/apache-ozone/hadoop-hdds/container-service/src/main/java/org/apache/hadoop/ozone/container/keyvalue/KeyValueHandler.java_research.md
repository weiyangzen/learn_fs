# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/KeyValueHandler.java

## Purpose
`KeyValueHandler` is the datanode orchestration layer for key-value containers. It dispatches container protocol commands, validates state and EC replica targeting, coordinates block/chunk managers, manages container lifecycle transitions, import/export/delete, checksum trees, and closed-container reconciliation.

## Important APIs, Types, And Functions
It extends `Handler` and owns `BlockManagerImpl`, a `ChunkManager`, `VolumeChoosingPolicy`, striped create locks, metrics, `ContainerChecksumTreeManager`, and `BlockInputStreamFactoryImpl`. Major methods include `dispatchRequest`, `handleCreateContainer`, `handlePutBlock`, `handleWriteChunk`, `handleReadChunk`, `handlePutSmallFile`, `handleGetSmallFile`, `handleCloseContainer`, `markContainerForClose`, `quasiCloseContainer`, `closeContainer`, `markContainerUnhealthy`, `deleteInternal`, `updateAndGetContainerChecksum`, `readBlock`, and `reconcileContainer`.

## Control Flow
`handle` calls `dispatchRequest`, which validates EC datanode UUIDs and switches by `ContainerProtos.Type`. Create builds `KeyValueContainerData`, serializes by container ID, creates storage, adds it to `ContainerSet`, and emits ICRs. Write flows require OPEN/CLOSING/RECOVERING state, validate checksum data when configured, delegate chunk IO to layout strategies, then persist block metadata through `BlockManager`. Reads validate BCSID/replica index, delegate to block/chunk managers, adapt old read protocol versions, and update metrics. Lifecycle flows lock containers, mark CLOSING/CLOSED/QUASI_CLOSED/UNHEALTHY, update checksum metadata, log transitions, and send ICRs. Reconciliation diffs local and peer Merkle trees, pulls peer chunks via `BlockInputStream`, writes them to closed containers, updates block metadata and checksum trees, then triggers scanner verification.

## State And Persistence
Persistent state includes container directories, chunk/block files, `container.yaml`, RocksDB tables, checksum tree files, finalized-block tables, and schema-v3 per-volume DB records. In-memory state includes lifecycle state, block statistics, BCSID, pending put-block cache, finalized local IDs, and data checksum. Delete removes DB/cache state, moves container data to deleted staging, then deletes content outside the write lock.

## Dependencies And Integration Points
The handler integrates `ContainerSet`, `VolumeSet`, `IncrementalReportSender`, Ratis `DispatcherContext`, `BlockUtils`, `ChunkUtils`, `KeyValueContainerUtil`, `KeyValueContainer`, SCM protocol response builders, checksum/Merkle classes, `DNContainerOperationClient`, Ozone client streams, security tokens, and upgrade/layout gates.

## Risks And Test Signals
Risks include state-gate mistakes, BCSID replay handling, delete locking/timeout behavior, partial reconciliation, checksum fallback correctness, and file/cache cleanup after failures. Test signals: idempotent create/close/delete replay, staged and combined writes, put/get small file, readBlock checksum alignment, EC replica-index rejection, checksum file fallback, force-delete and volume-failure paths, and reconciliation of missing/corrupt chunks.
