# sources/storage-engines/rocksdb/java/rocksjni/wal_filter_jnicallback.h

## Purpose
This header declares the C++ adapter that implements RocksDB `WalFilter` by calling a Java filter object.

## Important APIs, Types, and Functions
`WalFilterJniCallback` inherits from `JniCallback` and `WalFilter`. It declares overrides for `ColumnFamilyLogNumberMap`, `LogRecordFound`, and `Name`. Private state includes `std::unique_ptr<const char[]> m_name` and cached method IDs.

## Control Flow
The header defines the callback surface RocksDB will use during WAL recovery. Implementations must convert native maps, log metadata, and write batch pointers into Java callback parameters and convert Java decisions back to RocksDB enums.

## State and Persistence Behavior
State is limited to callback identity, cached method IDs, and immutable name. Persistence effects are indirect through WAL recovery decisions made by Java.

## Dependencies and Integration Points
It includes `rocksdb/wal_filter.h` and RocksJNI `jnicallback.h`. It is used by `wal_filter.cc` and `wal_filter_jnicallback.cc`, and integrates with Java `AbstractWalFilter`.

## Risks and Edge Cases
The callback object must outlive any RocksDB recovery path using it. Name and method ID initialization failures can leave an unusable adapter. The C++ and Java packed-result protocol must stay synchronized.

## Test Signals
Compile-time tests should catch signature changes in RocksDB `WalFilter`. Runtime tests should validate Java subclass dispatch, name stability, recovery decisions, and cleanup.
