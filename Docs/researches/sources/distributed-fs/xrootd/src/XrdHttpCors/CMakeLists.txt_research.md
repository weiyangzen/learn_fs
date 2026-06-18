# sources/distributed-fs/xrootd/src/XrdHttpCors/CMakeLists.txt

Purpose: Builds and installs the CORS HTTP extension plugin.

Important APIs/types/functions: Defines module target `XrdHttpCors-${PLUGIN_VERSION}`, compiles `XrdHttpCorsHandler.cc`, links `XrdUtils`, and installs the module to `${CMAKE_INSTALL_LIBDIR}`.

Control flow: The CMake file has no feature gating here; inclusion from the parent build determines whether it is evaluated.

State and persistence: Build metadata only.

Dependencies and integration points: Produces a dynamically loadable XRootD HTTP CORS plugin that exposes `XrdHttpCorsGetHandler`.

Risks: Missing source/header in the target list would break plugin ABI export at runtime. The target links only `XrdUtils`; if handler implementation starts using other non-header-only libraries, link dependencies must be updated.

Test signals: Configure/build with the plugin enabled, inspect the installed module name, and load it through the XRootD HTTP CORS configuration path.
