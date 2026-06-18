# sources/storage-engines/foundationdb/cmake/Findsccache.cmake

## Purpose
Finds `sccache` and configures it as the C/C++ compiler launcher.

## Important APIs, Types, and Functions
Sets `SCCACHE_EXECUTABLE`, `sccache_FOUND`, `CMAKE_C_COMPILER_LAUNCHER`, and `CMAKE_CXX_COMPILER_LAUNCHER`.

## Control Flow and Integration
When included, the module looks under `sccache_ROOT`/PATH and immediately mutates compiler launcher variables if found.

## State and Persistence
Depends on the `sccache` executable and CMake launcher support.

## Dependencies
State is CMake launcher variables; cache files are managed by sccache outside this script.

## Risks and Test Signals
Risks include global side effects when found and lack of package-handle standard args. Test signal is compiler commands routed through sccache.
