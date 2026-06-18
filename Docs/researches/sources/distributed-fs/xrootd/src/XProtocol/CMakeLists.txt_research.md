# sources/distributed-fs/xrootd/src/XProtocol/CMakeLists.txt

## Purpose
This CMake file attaches XRootD protocol source files to the `XrdUtils` library target.

## Important APIs, Types, and Functions
It calls `target_sources(XrdUtils PRIVATE XProtocol.hh XProtocol.cc)`.

## Control Flow
When the `XProtocol` subdirectory is processed, the protocol header and implementation are added to the already-defined `XrdUtils` shared library.

## State and Persistence
It mutates the build graph by adding sources to `XrdUtils`. No runtime persistence.

## Dependencies and Integration Points
Depends on the parent CMake file having created `XrdUtils`. It integrates protocol helper functions into the shared utility library used by broader XRootD components.

## Risks and Test Signals
If `XrdUtils` is renamed or not defined before this subdirectory is added, configuration fails. Build tests for `XrdUtils` cover this file.
