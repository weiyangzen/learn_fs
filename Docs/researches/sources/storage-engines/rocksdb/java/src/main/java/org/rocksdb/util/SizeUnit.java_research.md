# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/SizeUnit.java

## Purpose
`SizeUnit` defines binary size constants for Java code that configures RocksDB sizes.

## Important APIs and Types
Constants are `KB`, `MB`, `GB`, `TB`, and `PB`, each computed as powers of 1024. The private constructor prevents instantiation.

## Control Flow, State, and Persistence
There is no control flow or mutable state. Constants are compile-time/runtime Java values and do not persist any RocksDB state.

## Dependencies and Integration Points
No external dependencies. Tests and option code can use these constants for readability.

## Risks and Test Signals
The constants use `long` and remain within range through `PB`. No direct tests in this subset.
