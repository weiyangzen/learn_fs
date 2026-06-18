# sources/storage-engines/foundationdb/cmake/CompileBoost.cmake

## Purpose
Finds or builds the exact Boost 1.86.0 libraries required by FoundationDB, with special handling for sanitizers, libc++, Clang, Windows, and CI prebuilt roots.

## Important APIs, Types, and Functions
Defines `compile_boost(TARGET ...)`, imported static library targets for context/filesystem/iostreams/serialization/system/url/program_options, and interface targets `boost_target` and `boost_target_program_options`.

## Control Flow and Integration
The module first forces source builds for sanitizer configurations. Otherwise it looks under `/opt/boost_1_86_0*` and `BOOST_ROOT`, uses Boost config mode, then falls back to `ExternalProject_add` downloading Boost with a SHA256. The helper configures `user-config.jam` and b2 flags from compiler/linker settings.

## State and Persistence
Depends on Boost archive URL/hash, ExternalProject, CMake compiler/linker variables, zstd for Boost iostreams on some platforms, and sanitizer flag lists from `ConfigureCompiler.cmake`.

## Dependencies
State persists in `boost_install` under the build tree, imported target properties, and CMake prefix/hint variables.

## Risks and Test Signals
Risks include ABI mismatch between Clang/libc++ and GCC/libstdc++, stale prebuilt Boost, URL availability, and generator-expression flag drift. Test signals are `find_package(Boost)` success, ExternalProject byproducts, and downstream link of FDB targets.
