# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/CMakeLists.txt

## Purpose
This CMake file builds and installs the `fsalproxy_v3` loadable FSAL module. It defines compile flags, source membership, dependencies, sanitizer integration, link libraries, version metadata, and install destination.

## Important APIs, Types, And Functions
The build target sources are `main.c`, `nlm.c`, `rpc.c`, and `utils.c`, plus `$<TARGET_OBJECTS:nfs_mnt_xdr>`. The target is declared as `add_library(fsalproxy_v3 MODULE ...)`. It links `ganesha_nfsd`, `${SYSTEM_LIBRARIES}`, and `${LDFLAG_DISALLOW_UNDEF}`. When `USE_LTTNG` is enabled, it adds dependency on `gsh_trace_header_generate` and includes generated trace file properties.

## Control Flow
CMake adds `-D__USE_GNU`, defines the source list, creates the module target, applies sanitizer settings, conditionally wires LTTng generation, links required libraries, sets `VERSION 4.2.0` and `SOVERSION 4`, and installs the module into `${FSAL_DESTINATION}` as component `fsal`.

## State And Persistence
There is no runtime state here. The persistent artifact is the built module and its install metadata. The source list controls what code is included in the loadable FSAL.

## Dependencies And Integration Points
The target depends on generated XDR object code for NFS mount protocol, Ganesha server symbols, system RPC/socket libraries from `${SYSTEM_LIBRARIES}`, and optional trace-generation artifacts. The disallow-undefined linker flag is important because FSAL modules are dynamically loaded but should still resolve against expected server symbols.

## Risks
Adding a new source file to FSAL_PROXY_V3 without updating this list will omit it from the module. LTTng-specific generated property inclusion depends on `${CMAKE_BINARY_DIR}/gsh_lttng_generation_file_properties.cmake` existing when `USE_LTTNG` is true. `-D__USE_GNU` can affect system header feature exposure globally for this target.

## Test Signals
Build with and without `USE_LTTNG`, with sanitizers enabled, and with undefined-symbol disallowance. Verify the module installs into the configured FSAL destination and dynamically loads in a Ganesha runtime config using `FSAL { Name = PROXY_V3; }`.
