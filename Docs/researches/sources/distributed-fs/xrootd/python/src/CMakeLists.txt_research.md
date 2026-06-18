# sources/distributed-fs/xrootd/python/src/CMakeLists.txt

## Purpose
This CMake file builds the `client` Python extension module for PyXRootD.

## Important APIs, Types, and Functions
It calls `Python_add_library(client MODULE WITH_SOABI ...)` with all binding headers and source files, suppresses compile warnings with `target_compile_options(client PRIVATE -w)`, configures Apple RPATH/install-name properties, and links against XRootD client libraries.

## Control Flow
If CMake target `XrdCl` already exists, it links `client` against `XrdCl` and `XrdUtils`. Otherwise it discovers `XrdCl`, `XrdUtils`, and XRootD include directories via `find_library`/`find_path`, failing fast with `message(FATAL_ERROR)` when missing. For installed XRootD builds it adds both public and private include paths.

## State and Persistence
The build produces a Python extension named `client` with the interpreter ABI suffix. It mutates CMake target properties and include/link settings only during configure/generate.

## Dependencies and Integration Points
Depends on CMake's Python support, XRootD client libraries, `XrdUtils`, and private XRootD headers. It integrates with both in-tree XRootD builds and external/pre-installed XRootD builds.

## Risks and Test Signals
`-w` hides all compiler warnings and can mask Python C API reference issues. Private include dependency may break against installed XRootD layouts. Test signals are successful in-tree and external builds on Linux/macOS, import of the generated `client` module, and runtime smoke tests for `File`, `FileSystem`, `URL`, and `CopyProcess`.
