# sources/storage-engines/foundationdb/flow/bench/BenchHash.cpp

Purpose: benchmarks hashing throughput for Flow key-sized buffers using `hashlittle2`, CRC32C, and XXH3.

Important APIs/types/functions: enum `HashType`; template specializations `hash<HashLittle2>`, `hash<CRC32C>`, `hash<XXHash3>`; benchmark body `bench_hash`; helper `getString` from `BenchSupport.h`.

Control flow: each benchmark selects a byte length from `DenseRange(2, 18)` as `1 << range`, creates a deterministic `StringRef`, and repeatedly invokes the selected hash implementation with `DoNotOptimize` on results.

State/persistence: no persistent state. Data is generated once per benchmark state and then reused for all iterations.

Dependencies/integration: integrates Flow hash utilities (`flow/Hash3.h`, `flow/xxhash.h`), CRC32C, and Google Benchmark. Output is registered as template benchmarks for all three hash algorithms.

Risks: only measures single-buffer repeated hashing, so cache effects are favorable. The empty primary template would compile to no-op if accidentally used with an unhandled `HashType`.

Test signals: benchmark ranges span 4 bytes through 256 KiB and set item count to iterations, enabling comparative timing rather than byte-throughput counters.
