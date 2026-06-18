# sources/storage-engines/foundationdb/cmake/FDBBenchmark.cmake

## Purpose
Configures Google Benchmark as an interface dependency for FoundationDB benchmark targets.

## Important APIs, Types, and Functions
Defines `fdb_setup_googlebenchmark()` and interface target `fdb_google_benchmark`.

## Control Flow and Integration
The helper first chooses prebuilt roots under `/opt` based on compiler/libc++ mode, runs `find_package(benchmark)`, and links the imported target if found. If not, it configures and builds `benchmark-download.cmake`, adds the downloaded source subtree, and links the local `benchmark` target.

## State and Persistence
Depends on custom `Findbenchmark.cmake`, CMake generator availability, GitHub fetches, and benchmark CMake target names.

## Dependencies
State persists in downloaded googlebenchmark/googletest source/build directories and the `fdb_google_benchmark` target.

## Risks and Test Signals
Risks include configure-time network/build failures, prebuilt ABI mismatch, and old benchmark/googletest pins. Test signals are fdbrpc benchmark target configuration and successful benchmark executable link.
