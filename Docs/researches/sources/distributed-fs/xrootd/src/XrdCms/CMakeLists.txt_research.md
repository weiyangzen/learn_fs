# sources/distributed-fs/xrootd/src/XrdCms/CMakeLists.txt

## Purpose
Defines build integration for the XRootD cluster management service (`cmsd`), the XrdServer CMS client sources, and the local redirect plugin module.

## Important APIs, Types, and Functions
Adds CMS client/clustering source files to `XrdServer` with `target_sources()`. Defines the `cmsd` executable from Xrd core startup/config sources and many `XrdCms*` manager/server components. Defines the `XrdCmsRedirectLocal-${PLUGIN_VERSION}` module from `XrdCmsRedirLocal.cc/.hh`.

## Control Flow
CMake first attaches client-side CMS implementation files to the server library, then builds `cmsd`, applies GNU-specific `-msse4.2` as an interface compile option, links required libraries, and installs the executable and redirect-local plugin.

## State and Persistence Behavior
No runtime state. It controls build graph membership, linkage, and install destinations.

## Dependencies and Integration Points
Links `cmsd` against `XrdServer`, `XrdUtils`, thread, atomic, extra, and socket libraries. It integrates CMS code with top-level CMake variables such as `PLUGIN_VERSION`, `CMAKE_INSTALL_BINDIR`, and `CMAKE_INSTALL_LIBDIR`.

## Risks and Edge Cases
Source omissions here become link-time or runtime plugin availability failures. The GNU `target_compile_options(cmsd INTERFACE -msse4.2)` line may not apply as intended to the executable's own compilation because `INTERFACE` usage requirements are normally consumed by dependents.

## Test Signals
Build tests should verify `XrdServer`, `cmsd`, and `XrdCmsRedirLocal` build/install on supported compilers and platforms. Packaging checks should confirm installed binary and module names/locations.
