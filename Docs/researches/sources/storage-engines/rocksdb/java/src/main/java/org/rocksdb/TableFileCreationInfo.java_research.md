# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFileCreationInfo.java

## Purpose
`TableFileCreationInfo` is the detailed table-file creation event DTO, extending the brief info with file size, table properties, and operation status.

## Important APIs and Types
The protected JNI constructor forwards DB/cf/path/job/reason to `TableFileCreationBriefInfo` and stores `fileSize`, `TableProperties`, and `Status`. Getters expose these detailed fields; `equals`, `hashCode`, and `toString` are overridden.

## Control Flow
Construction performs superclass reason mapping, then stores detailed fields. Access is passive afterward.

## State and Persistence Behavior
It snapshots creation-event data; it does not modify created files or table properties. `TableProperties` and `Status` are held by reference.

## Dependencies and Integration Points
It integrates with RocksDB event listeners and table-property conversion. It depends on `TableFileCreationBriefInfo`, `TableProperties`, `Status`, and `TableFileCreationReason`.

## Risks and Test Signals
Tests should cover JNI construction, detailed status propagation on failed creation, and equality behavior. A notable risk is that `equals` and `hashCode` only compare subclass fields and ignore inherited DB name, column family, file path, job id, and reason, so two distinct file events can compare equal if their detailed fields match.
