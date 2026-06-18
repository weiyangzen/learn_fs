# sources/storage-engines/foundationdb/bindings/c/generate_asm.py

## Purpose
`generate_asm.py` scans `fdb_c.cpp` for versioned API-change macros and generates assembly trampolines plus a C++ header of function pointer globals. The trampolines make public C symbols dispatch to the selected API-version implementation at runtime.

## Important APIs, Types, And Functions
- The script takes `os`, `cpu`, `source`, `asm`, and `h` arguments.
- Regex `func_re` captures `FDB_API_CHANGED(func, ver)` and `FDB_API_REMOVED(func, ver)` lines.
- `write_windows_asm()` emits MASM procedures that jump through `fdb_api_ptr_<func>`.
- `write_unix_asm()` emits Linux/FreeBSD/macOS assembly for x86_64, aarch64, and ppc64le.
- The header defines `fdb_api_ptr_unimpl()`, `fdb_api_ptr_removed()`, `void* fdb_api_ptr_<func>`, and `<func>_v<ver>_PREV` macros.

## Control Flow
The script builds an ordered mapping of functions to API-change versions, opens output assembly and header files, writes platform-specific trampolines for each function, then emits pointer variables initialized to `fdb_api_ptr_unimpl` and compatibility macros pointing each changed function to its previous implementation name.

## State And Persistence Behavior
Generated files are build artifacts consumed by `fdb_c.cpp` and the assembler. No runtime state exists until the generated pointer variables are compiled into `libfdb_c`; those variables are updated by `fdb_select_api_version_impl()`.

## Dependencies And Integration Points
It depends only on Python `re` and `sys`, but semantically depends on macro formatting in `fdb_c.cpp` and platform calling conventions. CMake invokes it before building `fdb_c`.

## Risks And Edge Cases
Regex parsing is intentionally narrow; formatting changes to `FDB_API_CHANGED/REMOVED` lines could drop trampolines. Assembly correctness is architecture-sensitive, especially tail-call behavior and register preservation for arbitrary function signatures. ppc64le has custom stack/register handling that is higher risk than x86_64/aarch64.

## Test Signals
Build success on each platform is the first signal. Runtime API-version tests, legacy API tests, and upgrade/shim tests validate that generated trampolines dispatch to correct implementations.
