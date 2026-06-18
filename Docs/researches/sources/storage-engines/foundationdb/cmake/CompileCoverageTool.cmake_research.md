# sources/storage-engines/foundationdb/cmake/CompileCoverageTool.cmake

## Purpose
Builds the C# coverage tool used to generate per-target XML coverage metadata for Flow libraries and executables.

## Important APIs, Types, and Functions
Defines coverage tool source/project paths, the `coveragetool` target, `coveragetool_exe`, and cached `coveragetool_command`.

## Control Flow and Integration
On Windows it creates a CSharp executable target with .NET references. Under Mono it invokes `mcs` to produce `coveragetool.exe`. Otherwise it uses `dotnet_build`. `FlowCommands.cmake` later invokes `coveragetool_command` from `generate_coverage_xml`.

## State and Persistence
Depends on C# toolchain variables, Mono/dotnet support, and coverage tool source files under `flow/coveragetool`.

## Dependencies
Generated tool binaries persist in the CMake binary directory or dotnet project `bin` folder; command selection is cached internally.

## Risks and Test Signals
Risks include missing toolchain setup, command not set if platform branches change, and stale coverage XML. Test signals are successful `coveragetool` target build and generated `coverage.<target>.xml` files.
