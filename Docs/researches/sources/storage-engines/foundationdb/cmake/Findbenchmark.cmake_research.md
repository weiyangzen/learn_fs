# sources/storage-engines/foundationdb/cmake/Findbenchmark.cmake

## Purpose
Finds static Google Benchmark libraries and creates imported targets.

## Important APIs, Types, and Functions
Defines `_finalize_find_package_benchmark`, variables `benchmark_INCLUDE_DIR`, `benchmark_LIBRARY`, `benchmark_main_LIBRARY`, `benchmark_FOUND`, and targets `benchmark::benchmark`, `benchmark::benchmark_main`.

## Control Flow and Integration
The module looks for `benchmark/benchmark.h`, `libbenchmark.a`, and `libbenchmark_main.a` under `benchmark_ROOT`; early returns finalize negative discovery cleanly.

## State and Persistence
Depends on static benchmark library naming and root hints.

## Dependencies
No generated state; imported targets are configure-time state.

## Risks and Test Signals
Risks include only recognizing `.a` static names and not setting include dirs on `benchmark::benchmark_main`. Test signals are `FDBBenchmark.cmake` finding and linking benchmark targets.
