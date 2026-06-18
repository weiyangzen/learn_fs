# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteStallInfo.java

## Purpose
`WriteStallInfo` is an immutable Java data object describing a column family's write stall transition.

## Important APIs and Types
It stores `columnFamilyName`, `currentCondition`, and `previousCondition`. Getters expose each field. `equals`, `hashCode`, and `toString` support value comparisons and diagnostics.

## Control Flow, State, and Persistence
The package-private constructor is intended for JNI and tests. It converts condition bytes through `WriteStallCondition.fromValue`, so invalid native values fail during construction. The object is runtime event state only.

## Dependencies and Integration Points
Depends on `Objects` and `WriteStallCondition`. It likely integrates with RocksDB event listener callbacks for write stall changes.

## Risks and Test Signals
Risks are invalid native enum bytes and null/encoding behavior for column-family names. This subset includes no direct `WriteStallInfo` tests.
