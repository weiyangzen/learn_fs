# sources/storage-engines/rocksdb/cmake/modules/FindNUMA.cmake

## Purpose
Finds Linux NUMA support headers and library and exposes a CMake imported target for RocksDB's optional NUMA-aware features.

## Important APIs and Control Flow
`find_path(NUMA_INCLUDE_DIRS NAMES numa.h numaif.h HINTS ${NUMA_ROOT_DIR}/include)` and `find_library(NUMA_LIBRARIES NAMES numa HINTS ${NUMA_ROOT_DIR}/lib)` locate the dependency. `find_package_handle_standard_args` sets `NUMA_FOUND`. When found, `NUMA::NUMA` is created as an UNKNOWN IMPORTED target with include directories and library path.

## Dependencies, Risks, and Test Signals
The module uses optional `NUMA_ROOT_DIR` and CMake cache variables. It does not validate ABI or platform semantics. Risk is false positives on systems with partial NUMA headers/libraries or nonstandard library names. Coverage comes from CMake builds with `WITH_NUMA` enabled.
