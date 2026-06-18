# sources/distributed-fs/xrootd/src/XrdOfs/CMakeLists.txt

## Purpose
This CMake file wires the XrdOfs implementation into the `XrdServer` target and builds the `XrdOfsPrepGPI` module plugin.

## Important APIs, Types, and Functions
The build declarations add many `XrdOfs*.cc` and `XrdOfs*.hh` files to `XrdServer` with `target_sources()`. It sets `XrdOfsPrepGPI` to `XrdOfsPrepGPI-${PLUGIN_VERSION}`, creates a `MODULE` library from `XrdOfsPrepGPI.cc`, links it privately to `XrdUtils`, and installs it to `${CMAKE_INSTALL_LIBDIR}`.

## Control Flow and State
At configure/generate time, CMake attaches source files to an already-defined target and creates the plugin target. There is no runtime control flow or persistent application state in this file, but build output names depend on `PLUGIN_VERSION`.

## Dependencies and Integration Points
The file assumes `XrdServer`, `XrdUtils`, `PLUGIN_VERSION`, and install directory variables have been defined by parent CMake logic. XrdOfs code integrates with filesystem, TPC, events, stats, and security headers listed here.

## Risks and Test Signals
Risks are build-graph omissions and plugin install/link errors. Tests should include full configure/build, verifying `XrdServer` compiles with all listed sources, the module file name includes the plugin version, `XrdOfsPrepGPI` links only required private dependencies, and install rules place the module in the expected library directory.
