# sources/storage-engines/foundationdb/cmake/CompileZstd.cmake

## Purpose
Provides a helper to fetch and add zstd v1.5.2 to the FoundationDB build.

## Important APIs, Types, and Functions
Defines `compile_zstd()` and sets internal `ZSTD_LIB_INCLUDE_DIR`.

## Control Flow and Integration
The function declares zstd with FetchContent, populates it once, adds its `build/cmake` subdirectory, and suppresses selected Clang warnings on `zstd`, `libzstd_static`, and `zstd-frugal` targets.

## State and Persistence
Depends on GitHub zstd tag `v1.5.2`, FetchContent, and target names exported by zstd's CMake project.

## Dependencies
FetchContent state and zstd build artifacts persist in the binary tree; include path is cached internally.

## Risks and Test Signals
Risks include unpinned-by-hash FetchContent, target name changes upstream, and warning suppressions hiding real issues. Test signal is successful zstd target build and consumers finding `ZSTD_LIB_INCLUDE_DIR`.
