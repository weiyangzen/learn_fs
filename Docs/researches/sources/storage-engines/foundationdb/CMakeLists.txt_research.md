# sources/storage-engines/foundationdb/CMakeLists.txt

## Purpose
This is the top-level FoundationDB CMake build definition. It configures project metadata, build type, compiler/tooling, versioning, components, dependencies, subdirectories, testing, packaging, and IDE compile-command generation.

## Important APIs, Types, And Functions
It requires CMake 3.24.2, defines project `foundationdb` version 8.0.0, blocks in-source builds, exposes options such as `OPEN_FOR_IDE`, `AUTO_DISCOVER_UNIT_TESTS`, `USE_SCCACHE`, `WITH_ACAC`, `WITH_CSHARP`, `NO_MULTIREGION_TEST`, and `NO_RESTART_TEST`, and includes modules like `ConfigureCompiler`, `FDBComponents`, `CompileActorCompiler`, `FlowCommands`, `CompileBoost`, `GetFmt`, and `GetMsgpack`.

## Control Flow
Configuration sets a default build type, resolves C#/.NET/Mono tooling, builds or skips actor/compiler-related tools, generates version and cluster files, enables CTest, sets sanitizer environment options, adds core subdirectories, conditionally adds bindings/docs/packaging, and prints selected components.

## State And Persistence Behavior
It writes generated files into the build tree (`version.txt`, `versions.target`, `fdb.cluster`) and may generate a source-tree `compile_commands.json` when requested. It configures packaging and install layout but does not run builds itself.

## Dependencies And Integration Points
This file is the integration hub for Flow, fdbrpc, fdbclient, fdbserver, bindings, tests, documentation, Boost, fmt, msgpack, CPack/MSI packaging, Swift, C#, Python, and platform-specific options.

## Risks And Edge Cases
In-source builds fatal. Release builds reject ACAC. Explicit C# tool enablement without a toolchain is fatal, while implicit enablement can skip coverage tooling. Cross-compiling disables selected subdirectories. The version variables must stay aligned with release branches.

## Test Signals
Signals include CMake configure success, component printout, generated files, CTest registration, and downstream platform workflows such as Windows Boost CONFIG testing.
