# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteStallCondition.java

## Purpose
`WriteStallCondition` enumerates write controller states reported to Java listeners or info objects.

## Important APIs and Types
Values are `DELAYED`, `STOPPED`, and `NORMAL`, each backed by a native byte. Package-private `getValue()` and `fromValue(byte)` bridge native values.

## Control Flow, State, and Persistence
The enum is immutable. It represents runtime write stall state, not persistent data. `fromValue` scans constants and throws on unknown bytes.

## Dependencies and Integration Points
Used by `WriteStallInfo`, likely in event listener callbacks from native RocksDB.

## Risks and Test Signals
Byte mismatch would misreport stall states. This subset has no direct write stall tests.
