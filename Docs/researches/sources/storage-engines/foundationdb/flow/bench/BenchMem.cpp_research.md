# sources/storage-engines/foundationdb/flow/bench/BenchMem.cpp

Purpose: simple baseline benchmarks for standard `memcmp` and `memcpy` over 10,000-byte buffers.

Important APIs/types/functions: `bench_memcmp` and `bench_memcpy`, each registered with `BENCHMARK`.

Control flow: `bench_memcmp` allocates two buffers, zeroes both, changes the last byte of the second, and repeatedly compares the full range. `bench_memcpy` allocates source and destination buffers and repeatedly copies the fixed length.

State/persistence: all buffers are `std::unique_ptr<char[]>` local to each benchmark state. No durable state exists.

Dependencies/integration: uses `<cstring>`, `<memory>`, and Google Benchmark. It is separate from the more detailed `BenchMemcpy.cpp` matrix.

Risks: fixed-size, hot-cache behavior may not represent production memory patterns. `bench_memcpy` does not initialize the destination before use, which is fine for copy timing but not validation.

Test signals: basic benchmark names `bench_memcmp` and `bench_memcpy` provide coarse regression signals for libc or Flow memcpy override behavior.
