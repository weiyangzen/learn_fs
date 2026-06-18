# sources/storage-engines/foundationdb/cmake/FindGperftools.cmake

## Purpose
Finds gperftools tcmalloc/profiler support and exposes it as an imported target.

## Important APIs, Types, and Functions
Searches `GPERFTOOLS_TCMALLOC`, `GPERFTOOLS_PROFILER`, `GPERFTOOLS_TCMALLOC_AND_PROFILER`, `GPERFTOOLS_INCLUDE_DIR`, sets `GPERFTOOLS_LIBRARIES`, and creates imported target `gperftools`.

## Control Flow and Integration
When `USE_GPERFTOOLS` is enabled by `ConfigureCompiler.cmake`, `find_package(Gperftools REQUIRED)` invokes this module and fails if the combined library or headers are missing.

## State and Persistence
Depends on `Gperftools_ROOT_DIR`, `find_library`, `find_path`, and `FindPackageHandleStandardArgs`.

## Dependencies
No generated state; variables and imported target properties persist in the CMake configure.

## Risks and Test Signals
Risks include requiring `tcmalloc_and_profiler` even if separate libs exist, and root variable naming mismatch expectations. Test signal is successful required find and link of profiling builds.
