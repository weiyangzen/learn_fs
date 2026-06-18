# sources/storage-engines/foundationdb/cmake/Jemalloc.cmake

## Purpose
Builds a custom jemalloc 5.3.0 dependency when system jemalloc is not used.

## Important APIs, Types, and Functions
Creates interface `jemalloc`, imported `jemalloc::jemalloc`, imported `jemalloc_pic::jemalloc_pic`, and ExternalProject `Jemalloc_project`.

## Control Flow and Integration
If `USE_JEMALLOC` is off the module returns. Otherwise it downloads the pinned jemalloc tarball, configures static/profile-enabled jemalloc with current C/C++ compilers, runs make/install, and points imported targets at the produced libraries.

## State and Persistence
Depends on ExternalProject, make, configured compilers, and jemalloc release archive/hash.

## Dependencies
State persists in `${CMAKE_BINARY_DIR}/jemalloc` and imported target dependencies/properties.

## Risks and Test Signals
Risks include source build tool availability, static/PIC target assumptions, and profile-enabled build differences. Test signal is FDB link against `jemalloc::jemalloc` or PIC library.
