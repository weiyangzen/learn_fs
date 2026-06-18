# sources/distributed-fs/xrootd/src/XrdSut/CMakeLists.txt

## Purpose

This CMake fragment adds the XrdSut sources and headers to the `XrdUtils` target. XrdSut provides security utility support for bucketized authentication buffers, password-file persistence, cache entries, random helpers, and tracing.

## Important APIs, types, and functions

The fragment uses one `target_sources(XrdUtils PRIVATE ...)` call. It lists all implementation/header pairs in this work item plus `XrdSutRndm.hh` and `XrdSutTrace.hh`.

## Control flow

There is no runtime control flow. Build generation includes these files in the private source list for `XrdUtils`, so dependent libraries consume compiled symbols from `XrdUtils` rather than compiling XrdSut directly.

## State and persistence behavior

No runtime state is defined. Build state is the dependency relationship between `XrdUtils` and the listed files.

## Dependencies and integration points

This integrates XrdSut with the wider XRootD build. Security protocol implementations such as `XrdSecpwd` and `XrdSecgsi` depend on the resulting utility objects for buffer parsing, password-file access, caches, and random generation.

## Risks and edge cases

Adding a new XrdSut source/header without updating this list can produce link or install/build visibility failures. Since headers are marked private in `target_sources`, public installation/export behavior must be controlled elsewhere in the build system.

## Test signals

Build tests should verify `XrdUtils` compiles and links after any XrdSut file changes. Downstream security protocol build targets are the main integration signal.
