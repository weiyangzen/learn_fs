# sources/distributed-fs/xrootd/src/XrdOssStats/CMakeLists.txt

## Purpose
Builds and installs the `XrdOssStats` OSS plugin module.

## Important APIs and build flow
The script sets the module target name to `XrdOssStats-${PLUGIN_VERSION}` and creates a `MODULE` library from the stats config, file, and filesystem sources/headers. It links the plugin privately against `XrdServer` and `XrdUtils`. On non-Apple platforms it applies an ELF version script from `export-lib-symbols` to constrain exported symbols. Finally it installs the module to `${CMAKE_INSTALL_LIBDIR}`.

## Dependencies and integration
The target integrates into the broader XRootD plugin build and relies on `PLUGIN_VERSION`, `CMAKE_INSTALL_LIBDIR`, and core XRootD targets being defined by the parent CMake project.

## Risks and test signals
The most important build risk is symbol visibility: the plugin entry point must remain exported by the version script. Tests should build on Linux and macOS, inspect exported symbols for `XrdOssAddStorageSystem2`, and load the plugin in an XRootD configuration with `osslib`.
