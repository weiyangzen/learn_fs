<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/monitoring/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/monitoring/CMakeLists.txt

## Purpose
This CMake file builds the `ganesha_monitoring` shared library from the Prometheus exposer and dynamic metrics implementation.

## Important APIs, Types, and Functions
It sets `CMAKE_CXX_STANDARD 17`, defines `ganesha_monitoring_SRCS` as `prometheus_exposer.cc` and `dynamic_metrics.cc`, creates `add_library(ganesha_monitoring SHARED ...)`, optionally links `procps` and defines `HAVE_PROCPS` on Linux, applies sanitizers, sets `-fPIC`, adds the prometheus-cpp-lite include directory, appends strict C++ flags, and installs the library to `${LIB_INSTALL_DIR}`.

## Control Flow
Configuration is platform-dependent. On Linux it calls `find_library(PROCPS_LIB procps)` and either links/defines procps support or emits a warning. On non-Linux platforms it skips procps checks with a status message. The rest of the target setup is unconditional for this directory.

## State and Persistence Behavior
The file persists build-system state through target definitions, compile flags, include paths, linked libraries, and install rules in the generated build tree. It does not manage runtime state.

## Dependencies and Integration Points
It depends on the top-level CMake variables/functions `LINUX`, `add_sanitizers`, `PROJECT_SOURCE_DIR`, and `LIB_INSTALL_DIR`. It integrates with embedded ntirpc monitoring headers under `libntirpc/src/monitoring/prometheus-cpp-lite/core/include` and with platform procps when resource metrics are available.

## Risks and Edge Cases
`add_definitions(-DHAVE_PROCPS)` is directory-wide rather than target-scoped, which can leak into other targets configured from this directory context. Strict `-pedantic-errors -Werror -Wall -Wextra` can break builds on compiler/library warning drift. If procps is unavailable, memory/CPU metrics silently compile out after a warning. The include path is private but hard-coded to the source tree layout.

## Test Signals
Build tests should cover Linux with and without `procps`, and non-Linux configuration. Packaging tests should confirm `libganesha_monitoring` is installed when monitoring is enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/monitoring/CMakeLists.txt -->
