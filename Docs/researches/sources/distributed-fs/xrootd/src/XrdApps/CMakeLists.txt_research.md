# sources/distributed-fs/xrootd/src/XrdApps/CMakeLists.txt

## Purpose

`XrdApps/CMakeLists.txt` defines XRootD application utilities, client plugins, replay tooling, and optional non-client-only executables. The file was read completely.

## Important APIs, Types, and Functions

It builds shared library `XrdAppUtils` from copy/config and multiplexed XML helpers, module plugins `${XrdClProxyPlugin}` and `${XrdClRecorder}`, executable `xrdreplay`, and, when `NOT XRDCL_ONLY`, tools such as `cconfig`, `mpxstats`, `wait41`, `xrdacctest`, `xrdadler32`, `xrdcks`, `xrdcrc32c`, `xrdmapc`, `xrdpinls`, `xrdprep`, and `xrdqstats`. It sets SOVERSION/VERSION for `XrdAppUtils` and installation targets.

## Control Flow

CMake first defines common app utilities and client-side plugins, then installs them. The `NOT XRDCL_ONLY` block adds server/full-build utilities and installs a subset of them.

## State and Persistence Behavior

This file mutates the CMake build graph and install manifest. There is no runtime state.

## Dependencies and Integration Points

Targets link against `XrdUtils`, `XrdCl`, `XrdServer`, `XrdPosix`, `XrdAppUtils`, `ZLIB::ZLIB`, thread libs, socket library, and `${EXTRA_LIBS}`. Plugin names include `${PLUGIN_VERSION}`, so packaging layout depends on global version variables.

## Risks and Edge Cases

Some executables are defined but not included in the shown install list (`xrdprep` and `xrdqstats` are built after the listed install block starts but are not in its target list here), which may be intentional or an install omission. Conditional `XRDCL_ONLY` builds must not reference server-only libraries. Link dependencies must stay consistent with source additions.

## Test Signals

CMake tests should cover full and `XRDCL_ONLY` configurations, plugin filename/version generation, installation manifests, and link success for each executable.
