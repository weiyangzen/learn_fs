# sources/storage-engines/foundationdb/cmake/EnableCsharp.cmake

## Purpose
Selects the C# build path for FoundationDB build tools.

## Important APIs, Types, and Functions
Calls `enable_language(CSharp)` on Windows, otherwise tries `find_package(dotnet 9.0)` and falls back to required Mono, setting `CSHARP_USE_MONO`.

## Control Flow and Integration
The module returns after the first valid branch. If neither dotnet nor Mono is found on non-Windows, configure fails.

## State and Persistence
Depends on custom `Finddotnet.cmake`, `Findmono.cmake`, CMake CSharp language support, dotnet 9.0, and Mono `mcs`/runtime.

## Dependencies
State is held in CMake language enablement and `CSHARP_USE_MONO`; downstream modules use discovered executable variables.

## Risks and Test Signals
Risks include no explicit `CSHARP_TOOLCHAIN_FOUND` set here, dotnet version parsing ambiguity, and platform-specific CSharp behavior. Test signals are actor compiler, coverage tool, and vexillographer builds.
