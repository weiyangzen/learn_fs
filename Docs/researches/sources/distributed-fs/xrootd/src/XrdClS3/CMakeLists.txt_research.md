# sources/distributed-fs/xrootd/src/XrdClS3/CMakeLists.txt

## Purpose

This CMake file builds and installs the XRootD S3 client plugin. It conditionally enables the plugin based on libcurl availability and packages S3 file/filesystem/factory/download code into a versioned module.

## Important APIs, types, and functions

The script calls `find_package(CURL REQUIRED)` when `FORCE_ENABLED` is set and optional `find_package(CURL)` otherwise. If curl is unavailable, it returns early. It builds `XrdClS3Obj` as an object library from the S3 source/header set, links it privately with `XrdCl`, `XrdUtils`, `XrdXml`, `CURL::libcurl`, `OpenSSL::Crypto`, and `Threads::Threads`, forces PIC, then links a module library named `XrdClS3-${PLUGIN_VERSION}`.

On non-Apple platforms it applies the `configs/export-lib-symbols` version script and installs the module into `${CMAKE_INSTALL_LIBDIR}`.

## Control flow

The top-level source CMake adds this directory. If curl is found, object compilation and module creation proceed; otherwise the directory contributes no target. The module uses XRootD's plugin entry point exported by the factory implementation.

## State and persistence behavior

The file has no runtime state. Build outputs are the object library and installed plugin module.

## Dependencies and integration points

It depends on CMake targets for XRootD, libcurl, OpenSSL crypto, XML utilities, and threads. It includes the download handler, factory, file, and filesystem components, so build failures here catch cross-file API drift.

## Risks and edge cases

Optional curl discovery means S3 support can silently disappear unless `FORCE_ENABLED` is used. The version script is skipped on Apple, so exported symbol behavior differs by platform. Any new S3 source file must be added to `XrdClS3Obj`.

## Test signals

The primary signal is configuring/building with and without curl, with `FORCE_ENABLED` both true and false, plus install layout verification for the versioned module.
