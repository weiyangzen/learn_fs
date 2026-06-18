# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstPartitionerFactory.java

## Purpose
`SstPartitionerFactory` is the abstract Java handle type for native SST partitioner factories used from `ColumnFamilyOptions`.

## Important APIs and Types
It extends `RocksObject` and exposes only a protected constructor accepting a native handle. Concrete subclasses provide allocation and disposal.

## Control Flow
There is no behavior beyond `RocksObject` initialization. Native factory handles are passed through subclasses to options code.

## State and Persistence Behavior
The only state is the owned native handle. It does not persist data and does not define partitioning itself.

## Dependencies and Integration Points
It integrates with `ColumnFamilyOptions` and concrete factories such as `SstPartitionerFixedPrefixFactory`.

## Risks and Test Signals
Tests should verify option wiring keeps the factory alive long enough for native use and that subclass disposal is correct. The base class is intentionally minimal, so most risk sits in native factory implementations.
