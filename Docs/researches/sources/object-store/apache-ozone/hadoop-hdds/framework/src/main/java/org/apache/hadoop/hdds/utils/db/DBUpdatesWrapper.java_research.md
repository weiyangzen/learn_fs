# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBUpdatesWrapper.java

## Purpose
`DBUpdatesWrapper` is a simple mutable carrier for RocksDB WAL update batches returned by `DBStore.getUpdatesSince`.

## Important APIs and Types
It stores a `List<byte[]>` of write batch data, `currentSequenceNumber`, `latestSequenceNumber`, and a success flag. `addWriteBatch` appends data and advances current sequence number when the input sequence is newer.

## Control Flow and State
The wrapper starts with sequence numbers `-1` and success true. Callers add batches, set latest/current sequence values, and mark DB update success false on partial/failure cases.

## Persistence, Dependencies, and Integration
It does not persist state itself but transports persisted WAL bytes to Recon or other consumers. It is populated by `RDBStore.getUpdatesSince`.

## Risks and Test Signals
The returned data list is mutable and directly exposed. Sequence semantics rely on callers passing monotonically meaningful sequence numbers. Tests should cover empty wrapper defaults, add/update sequence behavior, success flag propagation, latest sequence setting, and external list mutation expectations.
