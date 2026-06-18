# sources/storage-engines/foundationdb/bindings/c/fdb_c_shim.cpp

## Purpose
`fdb_c_shim.cpp` supplies the custom dynamic-loading callback and override API used by the Linux/Unix C shim library. The shim lets an application link to a stable shim while selecting the actual `libfdb_c` implementation at runtime.

## Important APIs, Types, And Functions
- `fdb_shim_set_local_client_library_path(const char* filePath)` stores a process-global override path.
- `fdb_shim_dlopen_callback(const char* libName)` chooses the library path from the explicit override, `FDB_LOCAL_CLIENT_LIBRARY_PATH`, or the generated import library's default name, then calls `dlopen(..., RTLD_LAZY | RTLD_GLOBAL)`.
- `FDB_LOCAL_CLIENT_LIBRARY_PATH_ENVVAR` names the environment override.

## Control Flow
At runtime, generated shim trampoline code calls `fdb_shim_dlopen_callback()` when it needs to load the real client library. The callback gives precedence to the setter, then environment variable, then original library name. Unsupported platforms hit a compile-time `#error`.

## State And Persistence Behavior
The only state is process-local `g_fdbLocalClientLibraryPath`; no database state is touched. The loaded shared object remains managed by the dynamic loader.

## Dependencies And Integration Points
It depends on `foundationdb/fdb_c_shim.h`, `<dlfcn.h>`, and `std::string`. CMake wires it into `fdb_c_shim` together with generated sources from `Implib.so`.

## Risks And Edge Cases
The setter writes a global string with no synchronization, so callers should configure it before concurrent API use. `dlopen` failures are returned as null and must be handled by generated shim/import-library code. `RTLD_GLOBAL` intentionally exposes symbols, which helps client loading but can create symbol-interposition concerns.

## Test Signals
`fdb_c_shim_tests.py`, shim unit tests, shim API tester, and `shim_lib_tester` exercise path selection and behavior against both current and alternate client libraries.
