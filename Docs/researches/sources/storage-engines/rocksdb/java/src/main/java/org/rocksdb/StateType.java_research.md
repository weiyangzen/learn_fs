# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StateType.java

## Purpose
`StateType` maps native RocksDB thread-state identifiers to Java enum values for thread-status reporting.

## Important APIs and Types
Values are `STATE_UNKNOWN` and `STATE_MUTEX_WAIT`, each with a byte value. Package-private `getValue()` returns the JNI code, and static `fromValue(byte)` maps a native byte back to the enum or throws.

## Control Flow
Mapping is a simple linear scan over enum values. Unknown values fail fast with `IllegalArgumentException`.

## State and Persistence Behavior
There is no mutable state or persistence. Enum byte values must remain synchronized with native RocksDB state constants.

## Dependencies and Integration Points
`ThreadStatus` uses `StateType.fromValue` during JNI object construction and `ThreadStatus.getStateName` passes `getValue()` back to native helpers.

## Risks and Test Signals
Tests should cover all native values, unknown-value failures, and version drift when native adds new states. Missing enum updates can break thread-status construction for newer native libraries.
