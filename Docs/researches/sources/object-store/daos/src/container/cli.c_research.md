# sources/object-store/daos/src/container/cli.c

Purpose: libdaos container client implementation. It implements DAOS container API task handlers for create, destroy, open, close, query, properties, ACLs, OID allocation, attributes, snapshots, epoch operations, handle serialization, and helper lookups.

Important APIs/types/functions: exported `dc_cont_init/fini`, `dc_cont_create/destroy/open/close/query/set_prop/update_acl/delete_acl/alloc_oids`, local/global handle conversion, attr APIs, snapshot APIs, `dc_cont_hdl2*` helpers, and `dc_cont_mark_all_slave`. Internal infrastructure includes `cont_task_priv`, `cont_rsvc_client_complete_rpc`, `cont_task_reinit`, `cont_req_prepare`, `cont_req_complete`, `dc_cont_alloc`, `dc_cont_props_init`, and `dc_cont_glob`.

Control flow: initialization queries supported container RPC protocol version and registers v8 or v9 formats. Most operations validate handles/arguments, choose the pool service rank, build a container RPC through `dc_cont_req_create`, attach operation-specific payload/bulk handles, register a completion callback, and send asynchronously. Completion callbacks run replicated-service leader handling, may reinitialize delayed tasks on retry/rechoose, copy results into user buffers, and release RPC/pool/container refs. Open creates a client `dc_cont`, refreshes pool map if needed, links into pool/container handle tables, initializes checksum/dedup/compression/encryption properties, and returns a handle. Close refuses open objects and unlinks handles.

State/persistence: client state lives in handle hash entries (`dc_cont`), pool container lists, checksummers, and global handle buffers. Persistent container metadata is owned by servers; client operations mutate it through RPC. `dc_cont_local2global` serializes handle UUIDs/capabilities/properties/min map version for cross-process use, while `global2local` reconstructs a slave handle.

Dependencies/integration: DAOS task scheduler, CART RPC/bulk, rsvc client, pool client/map refresh, ACL/prop helpers, checksum/dedup/compress/encrypt config, object OID generation, and `rpc.c` protocol definitions.

Risks: repeated async cleanup paths are reference-count sensitive. Attribute get/set/del duplicate names/values to avoid bad memory registration, but allocation callback ordering must remain correct. `dc_cont_set_prop` forbids immutable props and rewrites status pm_ver. `dc_cont_alloc_oids` talks to random UPIN targets and has separate stale-map retry logic. Unsupported rollback/subscribe/named snapshots return `-DER_NOSYS`. Protocol skew is handled only for current and previous versions.

Test signals: no tests in this subset. High-value tests include open/close refcount behavior, retry/rechoose callbacks, global handle round trips, attr bulk validation, immutable property rejection, stale map OID retry, and snapshot error cases.
