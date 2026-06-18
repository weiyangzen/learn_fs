# sources/storage-engines/foundationdb/fdbclient/bench/BenchIterate.cpp

Purpose: benchmarks iteration cost over two mutation-list representations: `Standalone<VectorRef<MutationRef>>` and `MutationList`.

Important APIs and control flow: overloaded `populate` functions fill the selected container with repeated `SetValue` mutations using fixed key/value buffers from `getKV`. The templated `bench_iterate` walks the container and passes each mutation to `benchmark::DoNotOptimize`.

State and persistence: all mutations are in-memory and arena-backed. No database state is changed; the benchmark models transaction mutation payload traversal.

Dependencies and integration: includes `CommitTransaction.h`, `FDBTypes.h`, `MutationList.h`, `GlobalData.h`, Flow arena/allocator headers, and Google Benchmark. It is built into `fdbclient_bench`.

Risks: every mutation in a run has identical key and value references, so the benchmark isolates container traversal rather than data locality of diverse mutations. The `size` argument affects key/value length but not mutation count.

Test signals: registered ranges cover 1 to 1,048,576 mutations and 1 to 512 byte key/value sizes, reporting aggregate iteration throughput.
