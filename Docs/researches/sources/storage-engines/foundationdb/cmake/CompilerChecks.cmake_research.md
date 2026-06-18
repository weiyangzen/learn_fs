# sources/storage-engines/foundationdb/cmake/CompilerChecks.cmake

## Purpose
Collects small CMake compiler/toolchain decision helpers used by the main compiler configuration.

## Important APIs, Types, and Functions
Defines `env_set`, `default_linker`, `use_libcxx`, `static_link_libcxx`, and `check_swift_source_compiles`.

## Control Flow and Integration
`ConfigureCompiler.cmake` calls these helpers to turn environment variables into cache options, prefer LLD for Clang when present, default libc++ for Apple/Clang, decide when static C++ runtime linking is supported, and validate Swift snippets with `try_compile`.

## State and Persistence
Depends on CMake compiler IDs, `find_program`, `find_library`, and Swift/C++ compilers when Swift checks run.

## Dependencies
State is CMake cache variables produced by callers and temporary Swift files under `CMakeTmp`.

## Risks and Test Signals
Risks include decisions made before dependent options are initialized, environment overrides with unexpected values, and Swift try-compile behavior under cross-compilation. Test signals are configure messages and cache values used by `ConfigureCompiler.cmake`.
