# sources/storage-engines/foundationdb/cmake/Findjemalloc.cmake

## Purpose
Finds jemalloc headers/static libraries, preferring `jemalloc-config`, and creates imported targets.

## Important APIs, Types, and Functions
Defines macros to configure from `jemalloc-config`, create `jemalloc::jemalloc` and `jemalloc_pic::jemalloc_pic`, and finalize package results.

## Control Flow and Integration
The module first asks `jemalloc-config` for include/lib/version data and locates static libraries. If that fails, it searches headers and `libjemalloc.a`/`libjemalloc_pic.a` manually.

## State and Persistence
Depends on `jemalloc_ROOT`, `jemalloc-config`, static jemalloc libraries, and `FindPackageHandleStandardArgs`.

## Dependencies
No file persistence; imported targets and cache variables carry discovery state.

## Risks and Test Signals
Risks include a typo in `jemalloc_pic_LIBRARTY` target property, possible requirement of PIC library even when not needed, and static-only naming. Test signals are `find_package(jemalloc 5.3.0 REQUIRED)` success or fallback to `Jemalloc.cmake`.
