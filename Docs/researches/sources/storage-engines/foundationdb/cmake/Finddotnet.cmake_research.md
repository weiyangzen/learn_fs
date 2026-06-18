# sources/storage-engines/foundationdb/cmake/Finddotnet.cmake

## Purpose
Finds the dotnet executable and provides a helper to build .NET projects into predictable DLL outputs.

## Important APIs, Types, and Functions
Sets `dotnet_EXECUTABLE`, `dotnet_VERSION`, `dotnet_FOUND`, and defines `dotnet_build(project_file_path SOURCE ... CONFIGURATION ...)`.

## Control Flow and Integration
Discovery runs `dotnet` and captures output as a version string. `dotnet_build` computes the project stem and bin path, creates a custom command invoking `dotnet build --configuration ... --output ... --self-contained false -p:UseAppHost=false`, then exposes `<project>_EXECUTABLE_PATH`.

## State and Persistence
Depends on dotnet CLI, CMake `cmake_path`, project files, and source dependency lists.

## Dependencies
State persists in generated dotnet output directories and custom targets.

## Risks and Test Signals
Risks include weak version parsing, a likely `oneValueArg`/`oneValueArgs` typo affecting argument parsing, and stale project outputs if source lists are incomplete. Test signals are built actorcompiler/coveragetool/vexillographer DLLs.
