# sources/storage-engines/foundationdb/bindings/c/CMakeLists.txt

## Purpose
This CMake file builds FoundationDB's C client binding (`fdb_c`), generated API-version trampolines, option/version headers, unit and API tests, shim library, external workload libraries, and install/package metadata. It is the integration hub for the C binding.

## Important APIs, Types, And Functions
- `FDB_C_SRCS` lists the core C API implementation and public/internal headers.
- A custom command runs `generate_asm.py` to produce `fdb_c.g.S`/`.asm` and `fdb_c_function_pointers.g.h`.
- `vexillographer_compile()` generates `foundationdb/fdb_c_options.g.h`.
- `configure_file()` generates `fdb_c_apiversion.g.h` from `fdb_c_apiversion.h.cmake` and `FDB_API_VERSION_FILE`.
- `fdb_c` is built as `SHARED` outside `OPEN_FOR_IDE`.
- Non-Windows test targets include unit tests, API tester, Mako/performance tools, C90 header compatibility test, unavailable-cluster tests, client config tests, and upgrade tests.
- Linux builds generate and test `fdb_c_shim` through `Implib.so`.
- Install rules export `FoundationDB-Client`, headers, pkg-config/cmake config, direct library, and Linux shim.

## Control Flow
Configuration chooses OS/CPU, generated assembly output, platform-specific linker options, and test target shapes. Build flow generates headers/assembly before compiling `fdb_c`, links against `fdbclient`, optionally constrains exported symbols, then builds tests and external workload libraries. Test registration loops over TOML API-test files and creates Python venv tests, with ASAN and architecture filters.

## State And Persistence Behavior
Generated build artifacts include assembly trampoline source, function pointer header, generated option/version headers, copied external client library, shim generated sources, and package configuration files. Installation persists libraries and headers under client package locations.

## Dependencies And Integration Points
It integrates with repository CMake helpers (`vexillographer_compile`, `add_fdbclient_test`, `add_python_venv_test`, `fdb_install`), `fdbclient`, `flow`, `toml11`, `fmt`, `boost`, `SimpleOpt`, doctest, Python, and platform linkers. It also drives the API tester files in this subset.

## Risks And Edge Cases
Generated trampoline correctness is architecture-sensitive. Linker options differ for Apple/Linux/Windows, UBSAN, Clang 19, and portable static-libstdc++ builds. The Linux shim is not built on Windows or Apple. API tester registration depends on TOML globbing and explicit skip patterns. Installation must keep generated headers aligned with compiled library API versions.

## Test Signals
Configured tests include setup/unit tests, external-client unit tests, disconnected timeout tests, C API TOML workload tests, upgrade tests, shim library tests, C90 header compilation, and client config tests. These are strong signals for ABI, API-version compatibility, dynamic loading, and behavior under upgrades.
