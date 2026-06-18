# sources/storage-engines/rocksdb/cmake/modules/Findzstd.cmake

## Purpose
Finds the Zstandard compression library for RocksDB's optional zstd support.

## Important APIs and Control Flow
The module searches for `zstd.h` under `${zstd_ROOT_DIR}/include` and library `zstd` under `${zstd_ROOT_DIR}/lib`. `find_package_handle_standard_args(zstd ...)` sets `zstd_FOUND`. On success, it creates imported target `zstd::zstd` with location and include directory properties.

## Dependencies, Risks, and Test Signals
It integrates with `RocksDBConfig.cmake.in` through `find_dependency(zstd)`. Risks include no version validation and target naming compatibility with other zstd CMake packages. Compression-enabled build CI and downstream package discovery are the relevant tests.
