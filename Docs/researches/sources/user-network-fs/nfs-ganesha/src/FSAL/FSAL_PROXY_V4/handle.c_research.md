# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle.c

## Purpose
Implements FSAL_PROXY_V4 object handles and the NFSv4.1 RPC bridge. It translates FSAL operations into remote NFSv4 COMPOUND calls, manages the shared TCP RPC connection, negotiates and renews sessions, maps NFS errors/attributes to FSAL form, and builds local handles around remote filehandles.

## Important APIs, Types, and Functions
Important types are `proxyv4_rpc_io_context`, `proxyv4_handle_blob`, `proxyv4_obj_handle`, and `proxyv4_state`. Exported functions include `proxyv4_alloc_state`, `proxyv4_compoundv4_execute`, `proxyv4_init_rpc`, `proxyv4_close_thread`, `free_io_contexts`, `proxyv4_handle_ops_init`, `proxyv4_lookup_path`, `proxyv4_create_handle`, `proxyv4_get_dynamic_info`, and `proxyv4_wire_to_host`.

## Control Flow
`proxyv4_init_rpc` creates receiver and renewer threads plus per-slot IO contexts. FSAL object methods build COMPOUND arrays, call `proxyv4_nfsv4_call`, and translate the result. `proxyv4_compoundv4_execute` selects a free context, injects sequence slot/id values, sends the RPC, waits for the receiver to match a reply by XID, and returns NFS status.

## State and Persistence Behavior
Per-export state includes socket, XID, pending calls, free contexts, session/client ids, mutexes, conditions, and threads. Per-object state stores copied `nfs_fh4` bytes in a `proxyv4_handle_blob`, optional NFSv3 handle-map digest, and open flags. Optional persistent handle mapping is done through `HandleMap_SetFH` and `HandleMap_GetFH`.

## Dependencies and Integration Points
Integrates FSAL common ops, generated NFSv4 XDR/RPC code, auth-unix credentials, `op_ctx`, export manager state, conversion helpers, `fsal_nfsv4_macros.h`, and optional `handle_mapping`.

## Risks
The shared socket/XID/pending-call path is concurrency sensitive. Reconnects force outstanding calls to retry. Buffer sizing depends on export config. `readdir` performs a lookup per entry. Open-state support is incomplete in comments, and several methods omit parent pre/post attributes. Path lookup rejects `..` and does not follow intermediate symlinks.

## Test Signals
Signals include successful export startup, `EXCHANGE_ID`/`CREATE_SESSION`, lease renewal, root lookup, backend maxread/maxwrite capping, normal object operations against a remote NFSv4.1 server, and NFSv3 handle round trips when mapping is enabled.
