# sources/storage-engines/foundationdb/cmake/CompileVexillographer.cmake

## Purpose
Builds or selects the Vexillographer tool that generates FDB option bindings for C, C++, Java, Python, and Ruby.

## Important APIs, Types, and Functions
Defines `VEXILLOGRAPHER_COMMAND`, `VEXILLOGRAPHER_DEPENDS`, source/project variables, and `vexillographer_compile(TARGET LANG OUT OUTPUT ... ALL)`.

## Control Flow and Integration
The module prefers C# tooling when enabled: Visual Studio CSharp on Windows, Mono on Unix, or dotnet. If no C# toolchain is available it falls back to the Python implementation. `vexillographer_compile` emits custom commands that run the selected command over `fdb.options` and creates per-language custom targets.

## State and Persistence
Depends on `EnableCsharp.cmake`/toolchain discovery, Python3 fallback, `dotnet_build`, Mono, and `fdbclient/vexillographer/fdb.options`.

## Dependencies
State includes generated option files, built `vexillographer.exe`/DLLs, and cached command variables.

## Risks and Test Signals
Risks include language generator parity between C# and Python, missing dependency on generated outputs, and Windows/non-Windows branch drift. Test signals are generated options files and downstream binding builds.
