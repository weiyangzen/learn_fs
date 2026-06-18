<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/CMakeLists.txt -->
# sources/storage-engines/leveldb/CMakeLists.txt

## Purpose
Top-level CMake build definition for LevelDB 1.23.0, covering library, utility, tests, benchmarks, feature detection, optional third-party links, and install exports.

## Important APIs, Types, And Functions
Defines options `LEVELDB_BUILD_TESTS`, `LEVELDB_BUILD_BENCHMARKS`, `LEVELDB_INSTALL`; target `leveldb`; executable `leveldbutil`; helper functions `leveldb_test()` and `leveldb_benchmark()`; exported package namespace `leveldb::`.

## Control Flow
Sets C/C++ standards, detects platform/features/libraries, configures `port_config.h`, builds core sources and public headers into `leveldb`, conditionally adds platform env implementation, links optional crc32c/snappy/zstd/tcmalloc, adds tests/benchmarks, and installs targets plus CMake package files.

## State And Persistence Behavior
Build state is generated into `${PROJECT_BINARY_DIR}` including configured headers and package config files. Install state copies public headers and target exports to GNU install dirs.

## Dependencies And Integration Points
Uses CMake modules for include/library/symbol/compiler checks, Threads, googletest, google benchmark, optional sqlite3 and kyotocabinet, plus project source trees under db/table/util/helpers. Central integration point for all LevelDB C++ and C APIs, tests, benchmarks, CI workflow, and downstream `find_package(leveldb)` usage.

## Risks
Build behavior changes with detected optional libraries; shared builds hide symbols except exported API; some tests/benchmarks are skipped in shared builds or without optional dependencies.

## Test Signals
Adds aggregate `leveldb_tests`, C API test, platform env tests, and benchmark executables when enabled. CI runs these through CTest and benchmark steps.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/CMakeLists.txt -->
