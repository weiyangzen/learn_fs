# sources/distributed-fs/xrootd/src/XrdSsi/CMakeLists.txt

## Purpose
Builds the SSI libraries and server modules: the reusable SSI client/server support library, shared-memory map library, SSI filesystem module, and SSI logging module.

## Important APIs, Types, And Functions
- `XrdSsiLib` is a shared library containing alerting, atomics, client provider, request/response, service/session/task, logging, stats, and utilities.
- `XrdSsiShMap` is a shared library for shared-memory map support and links `ZLIB::ZLIB`.
- `${XrdSsi}` is a module containing SFS-facing SSI files, stat hooks, and configuration.
- `${XrdSsiLog}` is a module for logging integration.

## Control Flow
CMake creates targets, links them to `XrdCl`, `XrdUtils`, `XrdServer`, and zlib as needed, sets shared-library version properties on libraries, and installs all four runtime targets to the library directory.

## State And Persistence
No runtime state. Build outputs include shared libraries/modules whose names include `${PLUGIN_VERSION}` for modules.

## Dependencies And Integration Points
Integrates SSI with both XRootD client (`XrdCl`) and server (`XrdServer`) components. The SFS module links against `XrdSsiLib`, making the target files in this subset part of the core SSI runtime used by server plugins and client applications.

## Risks And Edge Cases
Target membership controls symbol availability across modules. Moving a source between `XrdSsiLib` and `${XrdSsi}` can change exported/loaded behavior. Missing version properties on modules may be intentional due plugin naming, but packaging should verify installed ABI expectations.

## Test Signals
Configure/build/install tests should validate all four targets, link dependencies, module names with plugin version, shared-library SONAME/version, and zlib availability for `XrdSsiShMap`.
