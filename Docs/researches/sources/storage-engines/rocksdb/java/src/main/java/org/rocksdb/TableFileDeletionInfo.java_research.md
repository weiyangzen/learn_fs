# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFileDeletionInfo.java

## Purpose
`TableFileDeletionInfo` is a value object describing a table-file deletion event.

## Important APIs and Types
It stores database name, deleted file path, job id, and `Status`. Public getters expose all fields, and it implements `equals`, `hashCode`, and `toString`.

## Control Flow
The package-private constructor is intended for JNI and testing. There is no native method or branch logic in the class itself.

## State and Persistence Behavior
It snapshots deletion-event data. The actual file deletion is performed by RocksDB native code; this class does not persist or delete anything.

## Dependencies and Integration Points
It integrates with event listener callbacks and uses `Status` to represent success or failure.

## Risks and Test Signals
Tests should cover event construction, failure status propagation, equality/hash/toString, and null handling. Since constructor access is package-private, JNI signature and tests must remain in sync.
