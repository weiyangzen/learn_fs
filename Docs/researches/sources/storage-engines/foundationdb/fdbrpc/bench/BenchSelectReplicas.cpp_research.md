# sources/storage-engines/foundationdb/fdbrpc/bench/BenchSelectReplicas.cpp

## Purpose
`BenchSelectReplicas.cpp` benchmarks `IReplicationPolicy::selectReplicas` for simple rack-across policies over synthetic locality maps.

## Important APIs, Types, and Functions
The central helper is `bench_select_replicas(int repCount, benchmark::State&)`, wrapped by `bench_select_replicas_tripple` and `bench_select_replicas_double`. It uses `PolicyAcross`, `PolicyOne`, `createTestLocalityMap`, `LocalityGroup`, and `LocalityEntry`.

## Control Flow
The benchmark constructs a rack policy, pre-warms `depth()` and `maxdepth()`, creates a synthetic locality map, copies entries into a vector sized by benchmark argument, and repeatedly clears the results vector before timing `policy->selectReplicas`. It registers triple-replica benchmarks with 4 and 8 servers and double-replica benchmarks with 2 and 8 servers.

## State and Persistence Behavior
State is in-memory and deterministic-random-derived through locality map creation. No persistent data is written.

## Dependencies and Integration Points
It depends on `fdbrpc/ReplicationPolicy.h`, `Replication.h`, `ReplicationUtils.h`, Flow arena support, and Google Benchmark. It directly reuses the replication utility test-map builder from this subset.

## Risks and Edge Cases
The synthetic topology is narrow and may not represent production locality diversity. The wrapper name `tripple` is misspelled but harmless. `SetItemsProcessed` is called inside the benchmark loop rather than after it, which is unusual for Google Benchmark usage.

## Test Signals
The main signal is measured `selectReplicas` throughput for fixed simple policies. Crashes or policy assertion failures indicate correctness issues in the selection path.
