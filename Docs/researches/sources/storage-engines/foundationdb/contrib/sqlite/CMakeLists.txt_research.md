# sources/storage-engines/foundationdb/contrib/sqlite/CMakeLists.txt

## Purpose
This CMake file defines FoundationDB's vendored SQLite static library target. It compiles the SQLite amalgamation with local headers and configures warning, clang-tidy, debug, memory-management, and compiler-specific flags suitable for third-party code embedded in the FoundationDB build.

## Important APIs, Targets, And Settings
- `add_library(sqlite STATIC ...)` creates a static target named `sqlite` from SQLite headers and `sqlite3.amalgamation.c`.
- Headers listed include `btree.h`, `hash.h`, `sqlite3.h`, `sqlite3ext.h`, `sqliteInt.h`, and `sqliteLimit.h`.
- `set_target_properties(sqlite PROPERTIES C_CLANG_TIDY "")` disables C clang-tidy for this third-party target.
- `target_include_directories(sqlite PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})` exposes the vendored SQLite directory to dependents.
- `target_compile_definitions(sqlite PRIVATE SQLITE_ENABLE_MEMORY_MANAGEMENT)` enables SQLite memory management support for the library build.
- On non-Windows platforms, Debug builds also define `NDEBUG`, and compile options add `-w` before other options to suppress third-party warnings.
- When `ICX` is true, `-fno-fast-math` is added because SQLite is not compatible with `-ffast-math`.

## Control Flow
CMake declares the static library, disables clang-tidy, exposes include directories, sets compile definitions, then conditionally adds platform/compiler flags. There are no source-generation, install, or test steps in this file.

## State And Persistence Behavior
This file only affects build-system state. It produces a static library artifact during the build and exports include usage requirements to dependents. Runtime persistence is SQLite's responsibility in consumers; this CMake target itself does not configure database files or runtime paths.

## Dependencies And Integration Points
The target is used by FoundationDB components that include or link SQLite. Nearby CMake references add `${CMAKE_SOURCE_DIR}/contrib/sqlite` to Swift interop include directories and link `sqlite` into `fdbserver_kvstore`. The public include directory makes `sqlite3.h` and related internal vendored headers available to consumers. The `SQLITE_ENABLE_MEMORY_MANAGEMENT` definition changes SQLite feature availability inside the compiled amalgamation.

## Risks And Edge Cases
- Defining `NDEBUG` for Debug builds on non-Windows suppresses assertions inside SQLite, which may hide third-party invariant failures during debug testing. This is probably intentional to avoid SQLite debug behavior but should be understood by maintainers.
- `-w` suppresses all warnings for the vendored C file, which keeps build output quiet but can mask compiler compatibility warnings after toolchain upgrades.
- `C_CLANG_TIDY` is cleared only for C; if future C++ sources were added, a separate CXX property might be needed.
- `ICX` must be defined by the outer build for the fast-math guard to trigger. If another compiler enables `-ffast-math`, SQLite may still be built with unsafe math flags.
- Listing headers in `add_library` helps IDE visibility but does not enforce header installation or ABI boundaries.

## Test Signals
Build validation should confirm the `sqlite` static target compiles on Windows and non-Windows toolchains and with ICX when enabled. Downstream link tests such as `fdbserver_kvstorelinktest` are important because `fdbserver_kvstore` links `sqlite`. Runtime storage-engine tests using SQLite-backed functionality provide the meaningful behavioral signal; this CMake file itself has no direct unit tests.
