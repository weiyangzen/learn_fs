# sources/storage-engines/foundationdb/contrib/TraceLogHelper/CMakeLists.txt

Purpose: CMake build glue for the C# TraceLogHelper library.

Important APIs and control flow: sets project source list, .csproj path, .NET references, and output DLL. If `CSHARP_USE_MONO` is true, adds a custom Mono compiler command and target; otherwise calls `dotnet_build` and exports `TraceLogHelperDll`.

State and persistence: produces `packages/bin/TraceLogHelper.dll` or the dotnet build executable path variable.

Dependencies and integration: requires CSharp compiler variables or repository `dotnet_build` function; source files include Event, JSON/XML parsers, assembly metadata, and utilities.

Risks and test signals: Mono branch references `${SRCS}` instead of the local source variable, which may rely on outer scope or be wrong. Build test both Mono and dotnet paths.
