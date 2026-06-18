# sources/storage-engines/foundationdb/bindings/c/foundationdb/fdb_c_shim.h

## Purpose
`fdb_c_shim.h` declares the public shim-only API for overriding which local `libfdb_c` library the generated shim loads at runtime.

## Important APIs, Types, And Functions
- `fdb_shim_set_local_client_library_path(const char* filePath)` sets an explicit client library path that overrides `FDB_LOCAL_CLIENT_LIBRARY_PATH`.
- `DLLEXPORT` is defined as empty unless provided by the build.

## Control Flow
Applications include this header and call the setter before selecting/using the C API through the shim. The implementation's `fdb_shim_dlopen_callback()` consults the stored path.

## State And Persistence Behavior
The header has no state. The implementation stores a process-global path. No database state is touched.

## Dependencies And Integration Points
It is installed only on Linux builds that include `fdb_c_shim`. CMake exports the shim target along with `FoundationDB-Client`.

## Risks And Edge Cases
The override must be set before the shim loads the real library to be effective. Passing null would be unsafe for the current `std::string` assignment implementation.

## Test Signals
Shim library tests and `shim_lib_tester` provide coverage for path override and dynamic loading behavior.
