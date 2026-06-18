# sources/distributed-fs/xrootd/src/XrdClHttp/CMakeLists.txt

## Purpose
This CMake file conditionally builds the `XrdClHttp` client plugin. It detects libcurl, builds an object library containing the HTTP plugin implementation, links required XRootD, curl, OpenSSL, XML, and thread dependencies, then packages a versioned module plugin for installation.

## Important Build APIs and Targets
`find_package(CURL)` is required only when `FORCE_ENABLED` is set; otherwise lack of CURL returns early and disables the plugin. `XrdClHttpObj` is an object library containing factory, file, filesystem, operation, options-cache, timeout parser, utility, and worker sources. The module library name is `XrdClHttp-${PLUGIN_VERSION}`. Non-Apple platforms add an export-symbol version script. Installed public headers include the connection callout, header callout, response info, and response wrappers.

## Control Flow
Configuration first resolves CURL availability, exits if unavailable, creates the object library, links private dependencies, marks object code position-independent, creates the module library from the object library, attaches export options where supported, and declares install rules.

## State and Persistence
Build state is limited to generated build-system targets. Installation persists the module under `${CMAKE_INSTALL_LIBDIR}` and selected public API headers under `${CMAKE_INSTALL_INCLUDEDIR}/xrootd/XrdClHttp`.

## Dependencies and Integration Points
The plugin depends on `XrdCl`, `XrdUtils`, `XrdXml`, `CURL::libcurl`, `OpenSSL::Crypto`, and `Threads::Threads`. Runtime entry point export is controlled by `configs/export-lib-symbols` on ELF platforms.

## Risks and Test Signals
If CURL is absent and `FORCE_ENABLED` is false, the plugin silently disappears. Source-list drift is a risk when adding new operation files. Build tests should cover optional and forced CURL modes, module symbol export, install header completeness, and link correctness on Apple versus non-Apple platforms.
