# sources/storage-engines/rocksdb/cmake/RocksDBConfig.cmake.in

## Purpose
Template for the installed CMake package configuration consumed by downstream `find_package(RocksDB)`. It reconstructs RocksDB's optional dependency graph based on configured build options and imports `RocksDBTargets.cmake`.

## Important APIs and Control Flow
The file starts with `@PACKAGE_INIT@`, extends `CMAKE_MODULE_PATH` with installed custom modules, and includes `CMakeFindDependencyMacro`. It sets `GFLAGS_USE_TARGET_NAMESPACE`, then conditionally calls `find_dependency` for JeMalloc, gflags, Snappy, ZLIB, BZip2, lz4, zstd, NUMA, and TBB according to `@WITH_*@` substitutions. gflags and Snappy prefer CONFIG packages and fall back to module mode. Threads is always required. Finally it includes exported targets and calls `check_required_components(RocksDB)`.

## Dependencies, Risks, and Test Signals
This file depends on the custom `cmake/modules/Find*.cmake` files being installed beside the package config. It persists no runtime state, but it encodes build-time feature state into the installed package contract. Risks include mismatches between exported target link interfaces and the conditional dependencies, and casing differences such as `lz4`/`zstd` target names. Validation usually comes from downstream CMake package tests or install/package CI.
