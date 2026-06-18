# sources/distributed-fs/xrootd/src/XrdOuc/CMakeLists.txt

## Purpose
Adds the XrdOuc utility sources to the `XrdUtils` target and builds the `XrdN2No2p` name-to-name plugin.

## Important build flow
The file first looks for system `nlohmann_json` 3.10.2. When present, it links `XrdUtils` publicly to `nlohmann_json::nlohmann_json` and defines `USE_SYSTEM_NLOHMANN_JSON`. `target_sources(XrdUtils PRIVATE ...)` then lists a large set of OUC implementation and header files, including argument parsing, backtrace, buffers, cache interfaces, CRC, environment/config helpers, JSON, name mapping, plugin loading, ranges, tokenizers, tracing, URIs, and miscellaneous utility containers.

At the end it creates `XrdN2No2p-${PLUGIN_VERSION}` as a module from `XrdOucN2No2p.cc`, links it against `XrdUtils`, and installs it to `${CMAKE_INSTALL_LIBDIR}`.

## Dependencies and integration
This is a central build manifest for the utility library used throughout XRootD. The optional JSON dependency changes compile definitions consumed by OUC JSON code.

## Risks and test signals
Because many headers are listed as private sources, IDE/export behavior depends on parent CMake conventions. Build tests should cover both bundled-json and system-json configurations, and plugin tests should confirm the `XrdN2No2p` module loads with the expected versioned name.
