# sources/distributed-fs/xrootd/src/XrdSecgsi/CMakeLists.txt

Purpose: Defines build targets for the GSI security protocol plug-in, its authorization mapping helper plug-ins, and optional GSI command-line utilities.

Important APIs and targets: Creates module libraries `${XrdSecgsi}`, `${XrdSecgsi_AUTHZVO}`, and `${XrdSecgsi_GMAPDN}`. Links the main GSI module to `XrdCrypto` and `XrdUtils`, and mapping modules to `XrdUtils`. Adds all three to the aggregate `plugins` target. Optionally builds `xrdgsiproxy` and `xrdgsitest` when `XRDCL_LIB_ONLY` is false.

Control flow: CMake evaluates target names with `${PLUGIN_VERSION}`, registers sources, links dependencies, installs module libraries to `${CMAKE_INSTALL_LIBDIR}`, and installs optional executables to `${CMAKE_INSTALL_BINDIR}`.

State and persistence: No runtime state. The file persists build graph membership and install layout.

Dependencies and integration points: Depends on `XrdSecProtocolgsi`, GSI option/trace headers, `XrdSecgsiAuthzFunVO`, `XrdSecgsiGMAPFunDN`, `XrdCrypto`, `XrdUtils`, and `OpenSSL::Crypto` for tools.

Risks: Source additions must be reflected here or the plug-in will miss symbols. Module names include `PLUGIN_VERSION`, so loader expectations and install names must stay aligned. Optional tools disappear in client-library-only builds.

Test signals: Configure with and without `XRDCL_LIB_ONLY`, build `plugins`, inspect installed module names, verify OpenSSL crypto linkage, and load the GSI protocol through the security protocol manager.
