# sources/storage-engines/wiredtiger/bench/workgen/CMakeLists.txt

## Purpose
This CMake file builds the Python workgen extension and supporting C++ library for POSIX WiredTiger builds when Python support is enabled.

## Important APIs, Types, and Functions
It selects `wiredtiger_static` with PIC or `wiredtiger_shared`, builds `workgen_cpp` from `workgen.cpp` and `workgen_func.c`, sets include directories and link libraries, configures SWIG flags, calls `swig_add_library(workgen TYPE ${share_state} LANGUAGE python SOURCES workgen.i)`, links generated module, and applies compiler/linker options.

## Control Flow
Non-POSIX builds return early. POSIX builds choose a link target, create a PIC static C++ helper library, hide libstdc++ symbols via `--exclude-libs`, configure SWIG interface name `_workgen`, include generated headers/configs, compile the Python extension, suppress SWIG wrapper warnings, and force `.so` suffix on Darwin.

## State, Persistence, and Dependencies
Build state includes `workgen_cpp`, `_workgen` Python extension, generated SWIG wrappers, and compiler flags. Dependencies include Python3, SWIG, WiredTiger library targets, `test_util`, generated headers, and POSIX support.

## Integration Points, Risks, and Test Signals
It integrates C++ workgen APIs with Python workloads under `bench/workgen/runner`. Risks include requiring PIC/shared builds, possible typo in `message(STATIC ...)`, and platform-specific dynamic-loading quirks. Signal is successful import of the generated `workgen` module.
