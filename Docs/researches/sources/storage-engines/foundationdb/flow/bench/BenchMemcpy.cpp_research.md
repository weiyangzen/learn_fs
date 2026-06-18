# sources/storage-engines/foundationdb/flow/bench/BenchMemcpy.cpp

Purpose: builds a detailed benchmark matrix comparing `rte_memcpy_noinline` and `std::memcpy` across sizes, cache locality modes, and alignment cases.

Important APIs/types/functions: enums `CopyFunction`, `CacheMode`, `CopyAlignment`; constants for small/large buffers, alignment, address count, and tested sizes; `AlignedBuffer`, `MemcpyBuffers`, `copy`, `benchMemcpy`, and registration helpers.

Control flow: global static registration creates variable-size and constant-size benchmarks for both copy implementations, four cache modes, and aligned/unaligned addresses. `MemcpyBuffers` preallocates 100 MiB large read/write buffers and 8 KiB small read/write buffers, fills deterministic read data, and precomputes randomized large offsets.

State/persistence: `memcpyBuffers()` owns a process-static buffer set reused by all benchmarks. Per-iteration state is an address index cycling through randomized offsets.

Dependencies/integration: uses Flow platform aligned allocation/free, deterministic random, `rte_memcpy_noinline` from `flow.cpp`, and Google Benchmark counters for bytes/items processed.

Risks: large static buffers affect process memory footprint and benchmark startup. Cache-mode simulation depends on buffer size and randomized offsets rather than explicit cache flushes. Constant-size template paths intentionally expose compiler specialization behavior.

Test signals: benchmark names are hierarchical under `Memcpy/<function>/<alignment>/<cache_mode>/variable|constant/<size>` with `MinTime(0.01)` and byte counters.
