# sources/storage-engines/foundationdb/fdbrpc/bench/CMakeLists.txt

## Purpose
This CMake file builds the `fdbrpc_bench` executable from all sources in the benchmark directory.

## Important APIs, Types, and Functions
It uses `include(FDBBenchmark)`, `fdb_find_sources(FDBRPC_BENCH_SRCS)`, `add_flow_target`, `fdb_setup_googlebenchmark`, `target_include_directories`, and `target_link_libraries`.

## Control Flow
CMake discovers benchmark sources, creates an executable target, sets up Google Benchmark, adds local include paths, and links threads, `fdb_google_benchmark`, `flow`, and `fdbrpc`.

## State and Persistence Behavior
It contributes build-system state only. Generated build artifacts are owned by the selected CMake build directory.

## Dependencies and Integration Points
It integrates with FoundationDB's CMake helpers and the shared Flow/fdbrpc libraries. The local include paths allow benchmark files to include `BenchSupport.h` and adjacent fdbrpc headers.

## Risks and Edge Cases
`fdb_find_sources` will include any new source dropped into the directory, which is convenient but can accidentally add experimental files. Include path `"${CMAKE_CURRENT_SOURCE_DIR}/include"` may be redundant unless a bench-local include directory exists.

## Test Signals
Successful configuration and build of `fdbrpc_bench` are the primary signals.
