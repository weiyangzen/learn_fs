# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TxnDBWritePolicy.java

## Purpose
`TxnDBWritePolicy` enumerates when transactional writes become visible in the underlying DB relative to commit/prepare phases.

## Important APIs and Types
Values are `WRITE_COMMITTED`, `WRITE_PREPARED`, and `WRITE_UNPREPARED`, each backed by a byte. `getValue()` exposes the JNI representation and `getTxnDBWritePolicy(byte)` maps native bytes back to enum values.

## Control Flow, State, and Persistence
The enum has immutable byte state. Conversion scans all values and throws `IllegalArgumentException` for unknown bytes. Persistence behavior is semantic rather than local: selected write policy determines whether only committed data, prepared data, or unprepared data can be written into DB storage.

## Dependencies and Integration Points
Used by `TransactionDBOptions.getWritePolicy/setWritePolicy` and native transaction DB configuration. It must remain byte-compatible with RocksDB C++ enum values.

## Risks and Test Signals
The main risk is byte drift between Java and native constants, which would misconfigure transaction durability/visibility. Unknown native bytes fail fast. This subset does not include direct tests for enum conversion.
