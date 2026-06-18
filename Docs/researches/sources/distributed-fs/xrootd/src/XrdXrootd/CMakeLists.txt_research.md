# sources/distributed-fs/xrootd/src/XrdXrootd/CMakeLists.txt

## Purpose

This CMake file defines the core XRootD protocol implementation sources compiled into `XrdServer` and builds the loadable `XrdXrootd-${PLUGIN_VERSION}` module.

## Important APIs, Types, and Functions

- `target_sources(XrdServer PRIVATE ...)`: registers protocol implementation files including admin, async I/O, bridge, config, file handling, monitoring, paging, prepare, protocol, redirect, response, stats, transit, and execution code.
- `set(XrdXrootd XrdXrootd-${PLUGIN_VERSION})`: names the protocol plugin module.
- `add_library(${XrdXrootd} MODULE XrdXrootdPlugin.cc)`: builds the loadable plugin.
- `target_link_libraries(${XrdXrootd} PRIVATE XrdServer XrdUtils ${EXTRA_LIBS})`: links the plugin against the server implementation and utilities.

## Control Flow

At configure/generate time, the listed sources become part of `XrdServer`. The plugin module is then built from `XrdXrootdPlugin.cc` and linked to the already-populated `XrdServer` target.

## State and Persistence Behavior

No runtime state exists here. Build state includes plugin naming, source membership, link libraries, and install destination.

## Dependencies and Integration Points

This is the central source registration point for XRootD protocol code. The admin files researched in this subset are compiled here into `XrdServer`, while the final module exposes the protocol plugin to the server runtime.

## Risks

- The large flat source list is easy to desynchronize when files are renamed or conditionally unavailable.
- The plugin link relies on `EXTRA_LIBS` supplied elsewhere, so missing platform dependencies can surface late.
- Admin and protocol internals are built into the same server target, which increases recompilation and integration coupling.

## Test Signals

Build tests should ensure all listed sources exist, the `XrdServer` target compiles, the plugin module links and installs to `${CMAKE_INSTALL_LIBDIR}`, and runtime plugin loading succeeds for `XrdXrootd-${PLUGIN_VERSION}`.
