# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindTcMalloc.cmake

## Purpose

`FindTcMalloc.cmake` discovers Google's tcmalloc allocator library for optional allocator replacement or profiling support.

## Important APIs, Types, and Functions

It exports `TCMALLOC_FOUND`, `TCMALLOC_ROOT_DIR`, `TCMALLOC_INCLUDE_DIR`, `TCMALLOC_INCLUDE_DIRS`, `TCMALLOC_LIBRARY`, and `TCMALLOC_LIBRARIES`. It uses environment fallback from `$TCMALLOC_ROOT_DIR`, `FIND_PATH`, `FIND_LIBRARY`, and `FIND_PACKAGE_HANDLE_STANDARD_ARGS`.

## Control Flow

If the CMake variable is absent but the environment variable exists, it seeds `TCMALLOC_ROOT_DIR`. It builds a search list including common system and package-manager locations, searches for `tcmalloc.h` under `include/tcmalloc`, searches for library `tcmalloc`, validates both, and populates plural variables on success.

## State and Persistence Behavior

Only CMake cache/configure variables are mutated and marked advanced. No targets are created.

## Dependencies and Integration Points

It depends on gperftools/tcmalloc development files. Higher-level build logic can link `${TCMALLOC_LIBRARIES}` and include `${TCMALLOC_INCLUDE_DIRS}` for allocator support.

## Risks and Edge Cases

The header can be packaged under `gperftools/tcmalloc.h` on some distributions, while this module looks for `tcmalloc.h` with a fixed suffix. It does not check allocator symbols or distinguish minimal/full/profiler variants.

## Test Signals

Configure with distro gperftools packages and custom `TCMALLOC_ROOT_DIR`, then link a target with `TCMALLOC_LIBRARIES`. Missing-header and missing-library cases should produce clear package-handle diagnostics.
