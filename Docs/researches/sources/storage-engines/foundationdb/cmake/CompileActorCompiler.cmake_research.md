# sources/storage-engines/foundationdb/cmake/CompileActorCompiler.cmake

## Purpose
Configures the actor compiler command used to translate `.actor.cpp` and `.actor.h` sources into generated C++ during Flow target builds.

## Important APIs, Types, and Functions
Defines Python source lists, legacy C# source lists, `ACTORCOMPILER_PY_COMMAND`, `ACTORCOMPILER_CSHARP_COMMAND`, `ACTORCOMPILER_COMMAND`, and the `actorcompiler` custom target.

## Control Flow and Integration
The module always creates a Python actor compiler target. If C# tools are enabled and found, it builds a C# actor compiler using MSBuild/CSharp on Windows, Mono, or `dotnet_build`; when present, the C# command overrides the Python command. `FlowCommands.cmake` consumes `ACTORCOMPILER_COMMAND` for generated actor files.

## State and Persistence
Depends on Python3, optional C# toolchain variables from `EnableCsharp.cmake`, Mono/dotnet helpers, and Flow actor compiler source files.

## Dependencies
State is stored in CMake cache/internal variables and generated executables such as `actorcompiler.exe` or dotnet output DLLs.

## Risks and Test Signals
Risks include divergent Python/C# compiler output, stale generated actor files, and missing `CSHARP_TOOLCHAIN_FOUND`. Test signals include actor generation custom commands and compare mode in `FlowCommands.cmake` when both compilers are available.
