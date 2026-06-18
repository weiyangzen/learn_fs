# sources/storage-engines/rocksdb/microbench/CMakeLists.txt

## Purpose
`microbench/CMakeLists.txt` defines CMake build rules for RocksDB microbenchmark executables.

## Important Commands
- `find_package(benchmark REQUIRED)` locates Google Benchmark.
- `find_package(Threads REQUIRED)` locates thread support.
- `file(GLOB_RECURSE ALL_BENCH_CPP *.cc)` discovers benchmark source files recursively under `microbench`.
- The `foreach` loop derives each executable target name from the source basename.
- Each target links `benchmark::benchmark`, `Threads::Threads`, `${ROCKSDB_LIB}`, and `${THIRDPARTY_LIBS}`.
- `add_custom_target(microbench DEPENDS ${ALL_BENCH_TARGETS})` creates an aggregate target.

## Control Flow and State
CMake configuration discovers all `.cc` files at configure time, creates one executable per file, appends each target to `ALL_BENCH_TARGETS`, and creates a single aggregate target. There is no runtime state.

## Dependencies and Integration Points
This file depends on Google Benchmark, CMake thread discovery, the RocksDB library target variable, and third-party library variables defined by the parent build. It is a build-system integration point for microbenchmark sources, separate from the gflags-based `memtablerep_bench.cc` in the memtable folder.

## Risks and Test Signals
`GLOB_RECURSE` means newly added benchmark files may require rerunning CMake configure before targets appear, depending on generator behavior. Target names are derived from basenames, so duplicate filenames in different subdirectories would collide. The aggregate `microbench` target provides a quick build signal that all discovered microbenchmarks compile and link.
