# sources/storage-engines/rocksdb/cmake/modules/Findgflags.cmake

## Purpose
Finds gflags headers and library for RocksDB tools/tests when a gflags CONFIG package is unavailable.

## Important APIs and Control Flow
`find_path(GFLAGS_INCLUDE_DIR NAMES gflags/gflags.h)` and `find_library(GFLAGS_LIBRARIES NAMES gflags)` locate dependency files. `find_package_handle_standard_args(gflags ...)` sets `gflags_FOUND`. If successful, it creates `gflags::gflags` as an UNKNOWN IMPORTED target with include directories, imported location, and `IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"`.

## Dependencies, Risks, and Test Signals
The installed RocksDB config tries config mode before falling back to this module. No runtime state exists. Risks include namespace selection mismatches with `GFLAGS_USE_TARGET_NAMESPACE`, missing multithreaded/static library variants, and no version validation. CI with gflags-enabled tools is the main test signal.
