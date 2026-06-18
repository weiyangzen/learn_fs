# sources/storage-engines/foundationdb/bindings/c/foundationdb/fdb_c_apiversion.h.cmake

## Purpose
`fdb_c_apiversion.h.cmake` is the template for generated `fdb_c_apiversion.g.h`. It publishes the latest C API version and specific option-introduction API versions to public headers.

## Important APIs, Types, And Functions
- `FDB_LATEST_API_VERSION` is substituted from `@FDB_AV_LATEST_VERSION@`.
- `FDB_LATEST_BINDINGS_API_VERSION` is substituted from `@FDB_AV_LATEST_BINDINGS_VERSION@`.
- `FDB_API_VERSION_CLIENT_TMP_DIR` and `FDB_API_VERSION_DISABLE_CLIENT_BYPASS` mark option introduction versions.

## Control Flow
CMake includes the repository API-version file, configures this template, and places the generated header under the build `foundationdb` include directory. `fdb_c.h` includes that generated file.

## State And Persistence Behavior
No runtime state exists. The generated header is a build artifact and installed header, so its values become part of the client compile-time contract.

## Dependencies And Integration Points
It depends on `CMakeLists.txt` providing the substitution variables through `FDB_API_VERSION_FILE`. It integrates directly with API-version validation in `fdb_c.h`.

## Risks And Edge Cases
If generated values lag or mismatch the compiled implementation, clients may compile with unsupported APIs or fail to access supported options. The template warns not to include the generated file directly, but consumers can still rely on macros through `fdb_c.h`.

## Test Signals
Build configuration and all C API compile tests indirectly validate this file. API-version selection tests catch mismatches between generated constants and implementation support.
