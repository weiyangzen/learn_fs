# sources/storage-engines/wiredtiger/test/windows/CMakeLists.txt

## Purpose
This CMake file builds the Windows test compatibility shim as a static library named `windows_shim`. The target packages POSIX-like APIs needed by WiredTiger tests and examples on Windows.

## Important APIs and targets
The only source is `windows_shim.c`. The target exports `${CMAKE_SOURCE_DIR}/test/windows` as a public include directory so consumers can include `windows_shim.h`, and privately includes generated build/config headers plus `src/include`. It applies `${COMPILER_DIAGNOSTIC_C_FLAGS}` to keep diagnostics consistent with the rest of the project.

## Control flow and behavior
CMake declares a `sources` list, creates `add_library(windows_shim STATIC ${sources})`, then attaches include directories and compile options. There is no conditional logic here; higher-level CMake decides when this directory participates in the build.

## State, dependencies, and integration
The static library is consumed by Windows test/example targets through `test_util.h`, which includes `windows_shim.h` under `_WIN32`. It depends on build-generated WiredTiger headers and source include paths because the shim calls some internal helpers such as error mapping and formatting.

## Risks and test signals
Risks are mainly build-graph related: missing public include exposure would break Windows test compilation, while missing private include directories would break references to `wt_internal.h`. Signals are successful Windows CMake configuration, `windows_shim` static-library compilation, and downstream test targets resolving POSIX compatibility symbols.
