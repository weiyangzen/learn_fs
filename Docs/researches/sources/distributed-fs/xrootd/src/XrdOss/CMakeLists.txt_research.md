# sources/distributed-fs/xrootd/src/XrdOss/CMakeLists.txt

## Purpose

`XrdOss/CMakeLists.txt` wires the default XRootD object storage system implementation into the `XrdServer` target and builds the GPFS stat plugin module.

## Important APIs, Types, and Functions

The file uses `target_sources(XrdServer PRIVATE ...)` to add default OSS sources and headers, then defines `XrdOssSIgpfsT-${PLUGIN_VERSION}` as a `MODULE` library from `XrdOssSIgpfsT.cc`, links it privately to `XrdUtils`, and installs it to `${CMAKE_INSTALL_LIBDIR}`.

## Control Flow

There is no runtime control flow. Build flow adds OSS implementation units such as `XrdOss.cc`, `XrdOssApi.cc`, `XrdOssAio.cc`, path/cache/copy/create/mss/rename/stat/unlink components, and related headers to the server build.

## State and Persistence Behavior

Build state is limited to CMake target membership and generated build-system metadata. No runtime persistence is defined here.

## Dependencies and Integration Points

The list is the integration point between XrdServer and the default OSS subsystem. The GPFS module integrates with plugin loading through XRootD versioned plugin naming.

## Risks and Edge Cases

Omitting a source here can silently remove runtime behavior from `XrdServer`; adding headers as private sources improves IDE visibility but does not compile them. Plugin naming depends on `PLUGIN_VERSION` being defined by the parent build.

## Test Signals

Build tests should verify `XrdServer` links with all OSS objects and that the GPFS module is produced and installed in the expected library directory.
