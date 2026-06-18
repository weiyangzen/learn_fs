# sources/distributed-fs/xrootd/src/XrdSecpwd/CMakeLists.txt

## Purpose
This CMake file builds the password-based XRootD security protocol plugin and, for full builds, the `xrdpwdadmin` administrative tool.

## Important APIs, types, and functions
The module target is `XrdSecpwd-${PLUGIN_VERSION}` and is built from `XrdSecProtocolpwd.cc`, `XrdSecProtocolpwd.hh`, and `XrdSecpwdPlatform.hh`. It links privately against `XrdCrypto`, `XrdUtils`, and `${CRYPT_LIBRARY}`. The target is added as a dependency of the aggregate `plugins` target and installed to `${CMAKE_INSTALL_LIBDIR}`.

When `XRDCL_LIB_ONLY` is false, the file also builds `xrdpwdadmin` from `XrdSecpwdSrvAdmin.cc`, links it with `XrdCrypto` and `XrdUtils`, and installs it to `${CMAKE_INSTALL_BINDIR}`.

## Control flow
Configuration always defines and installs the password plugin. The admin executable is conditional on building more than the client library subset.

## State and persistence behavior
No runtime state is managed here. Build outputs are the versioned plugin module and optionally the admin executable.

## Dependencies and integration points
The plugin depends on the XRootD crypto library because the password protocol performs key agreement and hashing. `${CRYPT_LIBRARY}` supplies platform `crypt()` support when available. `xrdpwdadmin` is the operational companion for creating or managing the password files consumed by the plugin.

## Risks and edge cases
The source header is listed as part of the module source set, which is harmless for IDE visibility but does not affect compilation behavior. If `${CRYPT_LIBRARY}` is empty on a platform where crypt-style passwords are enabled, link or runtime support may be incomplete. `XRDCL_LIB_ONLY` skips the admin tool, so deployments that need server-side password administration must ensure they are not using a client-only build.

## Test signals
Build tests should verify plugin compilation with and without a separate crypt library, installation of `XrdSecpwd-${PLUGIN_VERSION}`, and conditional presence of `xrdpwdadmin`. Runtime smoke tests should verify that the module can be dynamically loaded by XRootD and that `xrdpwdadmin` is available in non-client-only packages.
