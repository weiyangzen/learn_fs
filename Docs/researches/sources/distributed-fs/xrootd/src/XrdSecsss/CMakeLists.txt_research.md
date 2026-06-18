# sources/distributed-fs/xrootd/src/XrdSecsss/CMakeLists.txt

Purpose: build description for the SSS shared-secret security plugin and its administration utility.

Important targets: sets `XrdSecsss` to `XrdSecsss-${PLUGIN_VERSION}`. Adds support sources `XrdSecsssCon`, `Ent`, `ID`, `KT`, and `Map` to `XrdUtils`. Builds module library from `XrdSecProtocolsss.cc`, its header, and `XrdSecsssRR.hh`. Optionally builds `xrdsssadmin` when `XRDCL_LIB_ONLY` is false.

Control flow: target setup is straightforward: utility sources become part of `XrdUtils`, plugin module links `XrdCryptoLite` and `XrdUtils`, the umbrella `plugins` target depends on it, and install rules place module libraries and the admin executable in standard CMake install dirs.

State and persistence: no runtime state. It defines packaging/install topology and determines which SSS helpers are available to both the plugin and other XRootD components through `XrdUtils`.

Dependencies and integration: integrates with the repository-level `PLUGIN_VERSION`, `plugins` aggregate target, `CMAKE_INSTALL_LIBDIR`, and `CMAKE_INSTALL_BINDIR`. The admin tool only links `XrdUtils` because keytab logic is compiled there.

Risks: adding implementation files to `XrdUtils` broadens ABI and link exposure. `XRDCL_LIB_ONLY` disables the admin executable, so packaging tests should cover both client-only and full builds.

Test signals: configure/build with full and `XRDCL_LIB_ONLY` options, verify module name includes plugin version, confirm install paths, and run a link check for `xrdsssadmin`.
