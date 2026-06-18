# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindNTIRPC.cmake

## Purpose

`FindNTIRPC.cmake` discovers the libntirpc RPC implementation required by NFS-Ganesha. It supports `NTIRPC_PREFIX`, locates headers and libraries, reads a version macro, and exposes optional tracepoint/monitoring libraries when present.

## Important APIs, Types, and Functions

The module sets `NTIRPC_FOUND`, `NTIRPC_INCLUDE_DIR`, `NTIRPC_LIBRARY`, `NTIRPC_VERSION`, and optional `NTIRPC_TRACEPOINTS`, `NTIRPC_LTTNG`, and `NTIRPC_MONITORING`. It uses `find_path`, `find_library`, `file(READ)`, regex extraction, and `FIND_PACKAGE_HANDLE_STANDARD_ARGS`.

## Control Flow

With `NTIRPC_PREFIX`, discovery first searches only under that prefix. If include or library directories remain unset, it retries with default paths. It then finds `ntirpc` and optional support libraries in the detected library directory, reads `${NTIRPC_INCLUDE_DIR}/version.h`, extracts `NTIRPC_VERSION`, and validates the required include/library pair.

## State and Persistence Behavior

State is CMake cache/configure state only. Include and library variables are marked advanced. No targets or files are created.

## Dependencies and Integration Points

It depends on libntirpc headers containing `rpc/xdr.h` and library `libntirpc.so`. The detected values feed core RPC transport builds, and optional tracing libraries may be used when tracepoint support is enabled.

## Risks and Edge Cases

The module includes `LibFindMacros` but does not use it. `find_library(... NO_DEFAULT_PATH)` is used even when no custom directory was found, so a missing `NTIRPC_LIBRARY_DIR` can prevent default library discovery. Version extraction defaults to `0.0.0` when `version.h` is absent, which can make diagnostics less precise.

## Test Signals

Configure against a system libntirpc, a custom prefix, and a prefix containing only headers or only libraries. Build/link of the Ganesha RPC stack is the strongest integration signal, while configure logs should show the extracted `NTIRPC_VERSION`.
