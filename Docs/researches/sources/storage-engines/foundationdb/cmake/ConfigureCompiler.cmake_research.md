# sources/storage-engines/foundationdb/cmake/ConfigureCompiler.cmake

## Purpose
Centralizes FoundationDB compiler, linker, sanitizer, allocator, warning, debug-symbol, LTO, vector-instruction, libc++, pthread, and Swift compile settings.

## Important APIs, Types, and Functions
Defines many cache options through `env_set`, computes `USE_SANITIZER`, configures C/C++ standards, clang-tidy, linkers, sanitizer flags, Boost flag propagation, warning suppressions, architecture flags, DTrace/aligned allocation checks, and Swift C++ interop flags.

## Control Flow and Integration
The file includes `CompilerChecks`, sets defaults, validates incompatible options, finds required thread support, then branches heavily by Windows vs Unix and compiler family. Swift support appends target/sdk/resource/module-cache flags, imports cross-compile helper when needed, and verifies `import CxxStdlib`.

## State and Persistence
Depends on `FindThreads.cmake`, CMake check modules, optional Gperftools, LLD/libc++/libatomic, sanitizer runtimes, platform headers, and Swift toolchain metadata.

## Dependencies
State persists in CMake cache flags, global compile/link options, environment library paths for libc++, compile definitions, and Swift module cache paths.

## Risks and Test Signals
Risks are broad global side effects, duplicate/wrong flags for non-C++ languages, fragile compiler ID detection, and incompatible sanitizer/static-link configurations. Test signals are configure checks, compiler command lines, successful target builds, and sanitizer/Swift CI lanes.
