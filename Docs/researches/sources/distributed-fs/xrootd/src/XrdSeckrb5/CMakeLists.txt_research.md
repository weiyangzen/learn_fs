# sources/distributed-fs/xrootd/src/XrdSeckrb5/CMakeLists.txt

## Purpose
This CMake file builds and installs the Kerberos 5 security protocol plugin for XRootD. It is intentionally small and gates all work on the top-level `BUILD_KRB5` option.

## Important APIs, types, and functions
The build target is named `XrdSeckrb5-${PLUGIN_VERSION}` and is created as a `MODULE` library from `XrdSecProtocolkrb5.cc`. It links privately against `XrdUtils` and `${KERBEROS5_LIBRARIES}`, includes `${KERBEROS5_INCLUDE_DIR}`, and installs the resulting module library into `${CMAKE_INSTALL_LIBDIR}`.

## Control flow
Configuration returns immediately when `BUILD_KRB5` is false. Otherwise it defines the versioned plugin target, adds the module, configures link libraries and include directories, and installs it.

## State and persistence behavior
No runtime state is managed here. The only persistent effect is the generated plugin artifact in the build tree and its installation into the library directory.

## Dependencies and integration points
This file relies on top-level discovery of Kerberos include and library variables and on a project-wide `PLUGIN_VERSION`. The plugin target is expected to be dynamically loaded through XRootD's security plugin mechanism, where the exported C symbols in `XrdSecProtocolkrb5.cc` are discovered.

## Risks and edge cases
If Kerberos variables are unset or inconsistent while `BUILD_KRB5` is true, compilation or linking fails at this target. Unlike the password plugin CMake file, this file does not add an explicit dependency on a global `plugins` target, so packaging logic must not assume that dependency is present unless defined elsewhere. The module name includes the plugin version, so loader configuration must match the installed naming convention.

## Test signals
Build tests should verify both `BUILD_KRB5=OFF`, where the directory is skipped, and `BUILD_KRB5=ON`, where the module compiles and links with the platform Kerberos library. Install/package tests should confirm that `XrdSeckrb5-${PLUGIN_VERSION}` lands in the expected library directory and can be loaded by XRootD.
