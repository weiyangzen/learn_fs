# sources/distributed-fs/xrootd/src/XrdThrottle/CMakeLists.txt

Purpose: defines the `XrdThrottle-${PLUGIN_VERSION}` module target and its install rule.

Important APIs/types/functions: CMake creates a `MODULE` library from XrdThrottle sources plus `src/XrdOfs/XrdOfsFS.cc`, links privately to `XrdServer` and `XrdUtils`, adds the vendored `inih` include directory, and installs the module into `${CMAKE_INSTALL_LIBDIR}`.

Control flow: during configure/generate, the target name is computed from `PLUGIN_VERSION`; during build, listed sources are compiled into a loadable plugin rather than a normal shared library.

State and persistence: build artifacts are the module library and installed plugin file. No runtime state.

Dependencies and integration: integrates with the main XRootD CMake project, XrdOfs, XrdSfs, XrdUtils, XrdServer, and INIReader from `vendor/inih`.

Risks: adding `XrdOfsFS.cc` directly means the plugin target depends on OFS implementation internals. Missing `PLUGIN_VERSION` or vendor include layout breaks target naming/compilation. Source list must stay synchronized with new throttle headers and implementation files.

Test signals: configure/build the target, inspect module symbol exports, install path verification, and plugin loading in an XRootD runtime test.
