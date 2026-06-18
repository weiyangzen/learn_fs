# sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc.h

Purpose: declares the shared mdssvc data model, backend interface, constants, debug helper, and public entry points used by the mdssvc RPC server and search backends.

Important APIs and types: `slq_state_t` defines query lifecycle states from `SLQ_STATE_NEW` through running/results/full/done/end/error. `struct sl_query` is the central per-query object and carries backend-private data, context IDs, requested attributes, optional CNID restrictions, path scope, result buffers, timers, and list links. `struct sl_rslts` stores queued CNIDs and file metadata arrays. `struct sl_inode_path_map` backs later attribute fetches by mapping fake CNID/inode values to fake share paths and stat data. `struct mdssvc_ctx` is process-level backend state, while `struct mds_ctx` is per-tree-connect state including share path, authenticated SID/uid, iconv handles, VFS connection wrapper, query list, and inode map. `struct mdssvc_backend` is the backend vtable with `init`, `connect`, `search_map`, `search_start`, `search_cont`, and `shutdown`.

Control flow and integration: `mds_init()`, `mds_shutdown()`, `mds_init_ctx()`, `mds_dispatch()`, and `mds_add_result()` are exported to server glue and backends. Backends are expected to transition `sl_query` state and call `mds_add_result()` for filesystem paths that may be returned to clients.

State and persistence: the header makes clear that query and inode map state are per `mds_ctx`, not global durable data. The public constants cap result volume (`MAX_SL_RESULTS`, `SL_PAGESIZE`), runtime (`MAX_SL_RUNTIME`), and async timeout behavior.

Dependencies: includes mdssvc generated NDR definitions, marshalling/dalloc helpers, dlinklist, and works around GLib `TRUE`/`FALSE` macro conflicts before backend headers may include GLib users.

Risks: the header encodes ownership expectations but not locking; async backends must preserve talloc lifetimes. The `search_map` vtable member exists but is not assigned by the noindex/ES backends in this subset, so callers should not assume every function pointer is populated.

Test signals: compile-time tests should catch layout/API drift; behavioral tests should focus on state transition correctness and backend result ingestion through `mds_add_result()`.
