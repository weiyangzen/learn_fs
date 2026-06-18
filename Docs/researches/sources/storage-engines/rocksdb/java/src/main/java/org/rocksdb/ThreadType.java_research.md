# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ThreadType.java

## Purpose
`ThreadType` maps native RocksDB thread-pool/user-thread categories to Java enum values.

## Important APIs and Types
Values are `HIGH_PRIORITY`, `LOW_PRIORITY`, `USER`, and `BOTTOM_PRIORITY`. Package-private `getValue()` returns the native byte and static `fromValue(byte)` maps back.

## Control Flow
Mapping is a linear enum scan with `IllegalArgumentException` for unknown bytes.

## State and Persistence Behavior
There is no mutable state. Values describe monitoring snapshots only.

## Dependencies and Integration Points
`ThreadStatus` uses it during construction and for human-readable native name lookup.

## Risks and Test Signals
Tests should cover all mappings and unknown values. The primary risk is native enum expansion without Java update.
