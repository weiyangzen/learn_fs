# sources/storage-engines/rocksdb/cmake/modules/FindJeMalloc.cmake

## Purpose
Finds jemalloc headers and library for RocksDB builds and exports an imported target for link consumers.

## Important APIs and Control Flow
`find_path(JeMalloc_INCLUDE_DIRS NAMES jemalloc/jemalloc.h HINTS ${JEMALLOC_ROOT_DIR}/include)` locates headers, and `find_library(JeMalloc_LIBRARIES NAMES jemalloc HINTS ${JEMALLOC_ROOT_DIR}/lib)` locates the library. `find_package_handle_standard_args(JeMalloc ...)` defines `JeMalloc_FOUND`. On success, the module creates `JeMalloc::JeMalloc` as an UNKNOWN IMPORTED target with `IMPORTED_LOCATION` and `INTERFACE_INCLUDE_DIRECTORIES`.

## Dependencies, Risks, and Test Signals
Depends on CMake's `FindPackageHandleStandardArgs` and optional `JEMALLOC_ROOT_DIR`. It persists no state beyond CMake cache variables marked advanced. Risks are static/shared selection being delegated to `find_library`, no version checking, and imported target creation only if another target with the same name does not exist. Build CI with `WITH_JEMALLOC` provides coverage.
