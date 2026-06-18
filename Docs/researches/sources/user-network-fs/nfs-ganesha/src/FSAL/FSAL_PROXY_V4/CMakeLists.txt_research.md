# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/CMakeLists.txt

## Purpose
This CMake file builds and installs the `fsalproxy_v4` loadable FSAL module. It defines the module sources, optional handle-mapping sources, sanitizer integration, link libraries, optional sqlite dependency, version metadata, and install destination.

## Important APIs, Types, And Functions
The default source list is `handle.c`, `main.c`, `export.c`, and `xattrs.c`. When `PROXYV4_HANDLE_MAPPING` is enabled, `handle_mapping/handle_mapping.c` and `handle_mapping/handle_mapping_db.c` are appended. The target is declared as `add_library(fsalproxy_v4 MODULE ...)`, linked against `ganesha_nfsd`, `${SYSTEM_LIBRARIES}`, and `${LDFLAG_DISALLOW_UNDEF}`, and optionally `sqlite3`.

## Control Flow
CMake adds `-D__USE_GNU`, defines the source list, conditionally appends handle-mapping implementation, creates the module, applies sanitizers, links required libraries, adds sqlite when needed, sets `VERSION 4.2.0`/`SOVERSION 4`, and installs into `${FSAL_DESTINATION}`.

## State And Persistence
No runtime state is defined here. The optional handle-mapping build flag controls whether proxy v4 can persist or translate handles through sqlite-backed mapping code elsewhere.

## Dependencies And Integration Points
The module depends on Ganesha server symbols, system libraries, and optional sqlite. `export.c` references handle mapping under `PROXYV4_HANDLE_MAPPING`, so this build file must keep the conditional source and link dependency consistent with that preprocessor option.

## Risks
Mismatching `PROXYV4_HANDLE_MAPPING` with sqlite availability or source inclusion will break builds or runtime symbol resolution. New proxy v4 source files must be added here. Unlike the v3 build file, this file has no LTTng conditional block.

## Test Signals
Build both with and without `PROXYV4_HANDLE_MAPPING`, under sanitizer settings, and with undefined symbols disallowed. Verify the installed module loads and that sqlite is linked only in handle-mapping builds.
