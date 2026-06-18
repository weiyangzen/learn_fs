# sources/storage-engines/rocksdb/cmake/modules/FindSnappy.cmake

## Purpose
Finds the Snappy compression library when package-config mode is unavailable or not selected.

## Important APIs and Control Flow
The module searches for `snappy.h` under `${snappy_ROOT_DIR}/include` and the `snappy` library under `${snappy_ROOT_DIR}/lib`. `find_package_handle_standard_args(Snappy ...)` sets `Snappy_FOUND`. On success it creates `Snappy::snappy` as an UNKNOWN IMPORTED target with include directories and imported location.

## Dependencies, Risks, and Test Signals
This file integrates with `RocksDBConfig.cmake.in`, which first tries `find_dependency(Snappy CONFIG)` and then this module. It has no runtime persistence. Risks include no version/feature checks and target-name casing compatibility. Test signals include compression-enabled CMake builds and install-consumer package tests.
