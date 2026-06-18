# sources/storage-engines/rocksdb/cmake/modules/FindTBB.cmake

## Purpose
Finds Intel/oneAPI Threading Building Blocks for optional RocksDB parallelism support.

## Important APIs and Control Flow
If `TBB_ROOT_DIR` is unset, it is initialized from `$ENV{TBBROOT}`. The module searches for `tbb/tbb.h` and library `tbb`, with library hints including `${TBB_ROOT_DIR}/lib` and `ENV LIBRARY_PATH`. `find_package_handle_standard_args(TBB ...)` defines `TBB_FOUND`. On success, it creates imported target `TBB::TBB`.

## Dependencies, Risks, and Test Signals
State is confined to CMake variables and cache entries. Risks include modern TBB package layouts that prefer CONFIG packages, platform-specific library suffixes, and lack of version checks. Build coverage comes from `WITH_TBB` CMake configurations.
