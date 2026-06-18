# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/export.c

## Purpose
`FSAL_PROXY_V4/export.c` implements export-level configuration, creation, operation wiring, and release for the NFSv4 proxy FSAL. It parses per-export remote server/RPC/security/handle-mapping options, initializes RPC synchronization primitives, attaches the export to the FSAL module, optionally initializes handle mapping, starts the proxy v4 RPC/session machinery, and cleans all export resources on release or failure.

## Important APIs, Types, And Functions
`proxyv4_export_params` declares export config. Core fields include `Retry_SleepTime`, mandatory `Srv_Addr`, `NFS_Service`, `NFS_SendSize`, `NFS_RecvSize`, `NFS_Port`, `Use_Privileged_Client_Port`, and `RPC_Client_Timeout`. Under `_USE_GSSRPC`, it also supports Kerberos principal/keytab/lifetime/security type/active settings. Under `PROXYV4_HANDLE_MAPPING`, it supports handle mapping enablement plus database/temp directory, database count, and hash table size.

`remote_commit()` validates configured send/receive sizes against module maxwrite/maxread plus RPC header space. `proxyv4_export_init()` initializes session/clientid/list/context locks and condition variables and sets `rpc_sock = -1`. `proxyv4_export_destroy()` destroys those primitives. `proxyv4_release()` detaches, frees export ops, stops the close thread, frees I/O contexts, destroys locks/conds, and frees the export. `proxyv4_export_ops_init()` wires export operations. `proxyv4_create_export()` is the exported constructor.

## Control Flow
Export creation allocates and zeroes `struct proxyv4_export`, initializes proxy-private synchronization state, calls `fsal_export_init()`, loads config through `proxyv4_export_param`, initializes export ops, sets FSAL/upcall pointers, stores the export in `op_ctx`, and attaches it to the module. If handle mapping is compiled in and enabled/configured, it calls `HandleMap_Init()`. It then calls `proxyv4_init_rpc(exp)` to establish the NFSv4 proxy connection/session. On any post-attach failure it closes proxy threads, frees I/O contexts, detaches the export, frees ops, destroys synchronization primitives, and frees the object.

At runtime, the export ops delegate path lookup, wire/host handle conversion, handle creation, dynamic fs info, supported attrs, and state allocation to proxy v4 handle/module helpers. Release reverses initialization and ensures no close thread or I/O context remains before freeing locks.

## State And Persistence
Per-export state includes parsed remote connection parameters, RPC/session coordination fields, socket state, I/O contexts, condition variables, mutexes, and optional handle-map settings. Persistence exists only when handle mapping is compiled/enabled and its sqlite-backed implementation stores mappings in configured directories; this file only initializes that subsystem.

## Dependencies And Integration Points
The file depends on FSAL config/commonlib, export manager APIs, `proxyv4_fsal_methods.h`, `nfs_exports.h`, and `export_mgr.h`. It integrates with handle-level proxy v4 functions (`proxyv4_lookup_path`, `proxyv4_wire_to_host`, `proxyv4_create_handle`, `proxyv4_get_dynamic_info`, `proxyv4_alloc_state`, `proxyv4_init_rpc`, `proxyv4_close_thread`, `free_io_contexts`) and optional `HandleMap_Init()`.

## Risks
The `_USE_GSSRPC` `KeytabPath` config line appears to concatenate the default string and struct/type tokens without a comma, which is suspicious and should be compile-checked in Kerberos builds. `remote_commit()` depends on `op_ctx->fsal_module` being set during config commit. Resource cleanup is careful after `err_cleanup`, but failures before attach rely on the `err_free` path only. Handle mapping initialization failure after attach correctly detaches, but any partial HandleMap state cleanup is delegated elsewhere or absent here. Configured send/receive size validation prevents too-small buffers but does not validate remote behavior until `proxyv4_init_rpc()`.

## Test Signals
Test export creation with valid config, missing/invalid `Srv_Addr`, too-small send/receive sizes, RPC init failure, and release after successful init. Build and run `_USE_GSSRPC` config parsing tests. Build with `PROXYV4_HANDLE_MAPPING` and test handle-map init success/failure and cleanup. Runtime tests should verify release drains close threads and I/O contexts without leaked mutex/cond resources.
