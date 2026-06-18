# sources/storage-engines/foundationdb/cmake/Findmono.cmake

## Purpose
Discovers Mono runtime and C# compiler for non-Windows C# tool builds.

## Important APIs, Types, and Functions
Finds `MONO_EXECUTABLE` and `CSHARP_COMPILER_EXECUTABLE` (`mcs`), setting `mono_FOUND`.

## Control Flow and Integration
`EnableCsharp.cmake` requires this module when dotnet is unavailable, and C# compile modules use the executable paths to build and run tools.

## State and Persistence
Depends on `mono_ROOT` or PATH and the legacy `mcs` compiler rather than Microsoft `csc`.

## Dependencies
No persisted state beyond CMake variables.

## Risks and Test Signals
Risks include modern Mono distributions without `mcs`, and no standard package-handle diagnostics. Test signals are Mono messages and successful C# tool custom commands.
