# sources/distributed-fs/xrootd/src/XrdBwm/CMakeLists.txt

Purpose: defines the XrdBwm plugin build target.

Important APIs/types/functions: sets module target name `XrdBwm-${PLUGIN_VERSION}`; includes implementation, headers, policy, logger, handle, config, and trace files; links against `XrdServer`, `XrdUtils`, and thread libraries; installs the module into `${CMAKE_INSTALL_LIBDIR}`.

Control flow: CMake only. There are no conditional branches in this file; the parent build controls whether this directory is included.

State and persistence: no runtime state. Build output is a loadable module rather than a linked executable.

Dependencies and integration points: integrates with XRootD plugin naming/versioning conventions and server module loading. The included source list shows BWM is self-contained except for XRootD server/util dependencies and optional runtime-loaded auth/policy libraries.

Risks: because headers are listed as sources, IDE visibility is improved but behavior depends on CMake treating them as non-compilation units. Missing source entries would break plugin features at link time; no tests are declared here.

Test signals: configure/build with plugin version set, verify produced module name, link dependencies, install destination, and server-side load of `XrdSfsGetFileSystem`.
