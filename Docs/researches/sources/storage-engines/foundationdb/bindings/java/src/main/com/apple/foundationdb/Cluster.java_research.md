# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/Cluster.java

## Purpose
`Cluster` preserves the deprecated cluster-oriented API while delegating actual database opening to `FDB.open`. It gives old callers a `Cluster` object that records a cluster file path and executor without owning native cluster resources.

## Important APIs, Types, And Functions
`Cluster` extends `NativeObjectWrapper`, but its constructor passes `0`, making it immediately closed from the native-wrapper perspective. `options()` returns a no-op `ClusterOptions`. `openDatabase()` and `openDatabase(Executor)` call `FDB.instance().open(clusterFile, executor)`.

## Control Flow
Deprecated `FDB.createCluster` constructors instantiate `Cluster`; callers then call `openDatabase`, which re-enters the singleton `FDB` open path, starting the network if needed and creating an `FDBDatabase`.

## State And Persistence Behavior
State is limited to the Java-side `clusterFile`, `executor`, and no-op options object. `closeInternal` is empty because no native pointer is owned.

## Dependencies And Integration Points
It depends on `FDB`, `Database`, `ClusterOptions`, `Executor`, and `NativeObjectWrapper`. It exists for source/binary compatibility with applications written before direct database open was preferred.

## Risks And Edge Cases
Because the wrapper is constructed with pointer `0`, inherited closed-state behavior can surprise code that treats it like other native wrappers. Cluster options are silently no-op. Any failure in API initialization or network startup appears when `openDatabase` delegates to `FDB`.

## Test Signals
Tests should verify deprecated creation delegates to `FDB.open`, preserves custom executors and cluster file paths, and that closing a `Cluster` is harmless.
