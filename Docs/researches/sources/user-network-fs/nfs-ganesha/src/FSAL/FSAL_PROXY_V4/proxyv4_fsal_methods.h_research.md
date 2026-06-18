# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/proxyv4_fsal_methods.h

## Purpose
Shared internal declarations for FSAL_PROXY_V4 module, export, RPC, handle, xattr, and optional handle-map integration.

## Important APIs, Types, and Functions
Defines `proxyv4_fsal_module`, `proxyv4_client_params`, `proxyv4_export_rpc`, and `proxyv4_export`. Declares handle ops initialization, RPC lifecycle, xattr stubs, lookup/create-handle/dynamic-info/wire-to-host methods, export creation, and state allocation.

## Control Flow
Module init creates `PROXY_V4`; export creation fills `proxyv4_client_params` and initializes `proxyv4_export_rpc`; object methods recover `proxyv4_export` from `op_ctx->fsal_export`.

## State and Persistence Behavior
Describes all major per-export state: remote server parameters, Kerberos-related fields, optional handle-map params, client/session ids, socket/XID, pending calls, free contexts, threads, locks, and conditions.

## Dependencies and Integration Points
Depends on FSAL, pthread, dirent, bool, and optionally `handle_mapping.h`. Included by `main.c`, `export.c`, `handle.c`, and `xattrs.c`.

## Risks
RPC state is concurrency-heavy and must match init/destroy paths. `enable_handle_mapping` exists, but export code initializes mapping whenever compiled, suggesting the flag may not be honored.

## Test Signals
Compile-time consistency, export startup, thread creation, session establishment, and optional handle mapping round trips.
