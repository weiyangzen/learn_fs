# sources/user-network-fs/nfs-ganesha/src/idmapper/CMakeLists.txt

## Purpose
This CMake file builds the `idmap` object library, which contains Ganesha's NFSv4 owner/group ID mapping implementation and its caches, monitoring, and directory-service wrappers.

## Important APIs, Types, And Functions
It conditionally adds include directories for `${WBCLIENT_INCLUDE_DIR}` under `_MSPAC_SUPPORT` and `${DBUS_INCLUDE_DIRS}` under `USE_DBUS`. `idmap_STAT_SRCS` includes `idmapper.c`, `idmapper_cache.c`, `idmapper_negative_cache.c`, `idmapper_monitoring.c`, `pwnam_wrappers.c`, and `sss_nss_idmap.c`. The target is created with `add_library(idmap OBJECT ...)`, instrumented with `add_sanitizers`, and compiled with `-fPIC`.

## Control Flow, State, And Persistence
This is build configuration only. It selects include paths based on feature flags, defines the object library source set, and wires LTTng generated trace dependencies when tracing is enabled.

## Dependencies And Integration Points
The object library feeds Ganesha components that need UID/GID, owner string, cache, and monitoring logic. Feature flags integrate optional Winbind/MSPAC, DBus statistics, and generated LTTng trace support.

## Risks And Test Signals
Conditional includes must align with source-level `#ifdef` branches in `idmapper.c`; missing feature-specific headers will surface as build failures. Because the target is an object library, final link dependencies for DBus, Winbind, and libnfsidmap must be supplied by consumers.
