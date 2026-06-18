# sources/distributed-fs/xrootd/src/XrdSciTokens/CMakeLists.txt

## Purpose

This CMake fragment conditionally builds and installs the `XrdAccSciTokens` authorization plugin when SciTokens support is enabled and `SciTokensCpp` is available.

## Important APIs, Types, And Functions

- Clears `BUILD_SCITOKENS` cache state, returns early unless `ENABLE_SCITOKENS` is set.
- Uses `find_package(SciTokensCpp REQUIRED)` when `FORCE_ENABLED` is set, otherwise optional discovery.
- Defines module target `XrdAccSciTokens-${PLUGIN_VERSION}` from access, helper, and monitoring sources.
- Links against `XrdUtils`, `XrdServer`, `${SCITOKENS_CPP_LIBRARIES}`, thread libs, and dl libs.
- Adds include directories for vendored `inih`, `picojson`, and SciTokens headers.
- Defines `HAVE_SCITOKEN_CONFIG_SET_STR` when available and installs the module.

## Control Flow

Build flow is feature-gated. If SciTokens support is disabled or package discovery fails in non-forced mode, no plugin target is added. Successful discovery makes `BUILD_SCITOKENS` true and compiles the module.

## State And Persistence

The only persistent build state is the internal CMake cache variable `BUILD_SCITOKENS` and the installed shared module.

## Dependencies And Integration Points

This integrates with the project plugin build, SciTokens C++ library, XRootD server/utils targets, vendored INI/JSON parsers, and optional compile-time SciTokens configuration API availability.

## Risks And Edge Cases

- Optional discovery silently skips the plugin, so CI must assert `BUILD_SCITOKENS` when coverage is expected.
- Compile definitions and include variable names must match the `SciTokensCpp` package module.
- Runtime config behavior differs depending on `HAVE_SCITOKEN_CONFIG_SET_STR`.

## Test Signals

Build tests should cover disabled, optional-missing, forced-missing, and found SciTokens configurations. Runtime packaging should verify the module installs under `${CMAKE_INSTALL_LIBDIR}` and loads as `libXrdAccSciTokens`.
