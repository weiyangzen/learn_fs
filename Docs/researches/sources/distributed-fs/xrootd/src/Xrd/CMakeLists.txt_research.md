<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/Xrd/CMakeLists.txt

Purpose: declares the build membership for the core Xrd utility/server sources and the `xrootd` executable.

Important APIs/types/functions: not a C++ API, but it adds sources to `XrdUtils`, conditionally stops when `XRDCL_ONLY` is enabled, creates executable `xrootd` from `XrdConfig`, `XrdProtLoad`, `XrdStats`, and `XrdMain`, links runtime libraries, and installs the binary to `${CMAKE_INSTALL_BINDIR}`.

Control flow: CMake first appends many Xrd runtime sources to `XrdUtils`. If building client-only (`XRDCL_ONLY`), it returns before defining the server executable. Otherwise it defines and links `xrootd`.

State and persistence behavior: build-system state only. It controls which object files are linked into `XrdUtils` and whether the installed server binary exists.

Dependencies: depends on prior CMake definitions of `XrdUtils`, `XrdServer`, CMake install dirs, dynamic loader/thread/socket/extra libraries, and project option `XRDCL_ONLY`.

Integration points: integrates buffer, network, scheduler, poll, link, monitor, object, and trace code into `XrdUtils`; integrates daemon configuration and protocol loading into the executable. This file is the source of truth for whether changes in these `.cc`/`.hh` files are compiled into the server.

Risks: missing a source in `target_sources` can compile on some targets but fail link/runtime elsewhere. Header-only entries are useful for IDE visibility but not compilation. `XRDCL_ONLY` can hide server build failures in client-only CI lanes.

Test signals: configure/build both default and `XRDCL_ONLY`; verify `xrootd` links with `XrdServer`/`XrdUtils`; packaging/install tests check `${CMAKE_INSTALL_BINDIR}/xrootd`; CI should build server lanes after source-list changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/CMakeLists.txt -->
