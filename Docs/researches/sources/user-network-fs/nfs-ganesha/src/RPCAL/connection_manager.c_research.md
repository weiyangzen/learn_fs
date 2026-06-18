# sources/user-network-fs/nfs-ganesha/src/RPCAL/connection_manager.c

Purpose: implements a connection manager that attempts to ensure a client is connected to only one Ganesha server at a time, supporting local draining, remote drain/register callbacks, transport lifecycle hooks, metrics, and tracepoints.

Important APIs and types: `connection_manager__callback_set()`, `connection_manager__callback_clear()`, `connection_manager__client_init()`, `connection_manager__client_fini()`, `connection_manager__drain_and_disconnect_local()`, `connection_manager__connection_init()`, `connection_manager__connection_started()`, `connection_manager__connection_finished()`, `connection_manager__init()`, `connection_manager__client_t`, `connection_manager__connection_t`, callback context types, and state/result enums.

Control flow: each client moves through `DRAINED -> ACTIVATING -> ACTIVE -> DRAINING` with guarded transitions in `change_state()`. Starting a managed connection obtains/creates the `gsh_client`, initializes the connection object from transport custom data, and under the client mutex either activates a drained client by invoking the registered remote drain callback, waits for another activator, accepts an already active client, or cancels an ongoing drain. Registration happens through callbacks under a global rwlock; if the client drains while registration is in flight, the connection is deregistered and refused. Local drain marks connections destroyed, sets TCP linger to force fast close, calls `SVC_DESTROY()`, waits on a condition variable, and classifies success, timeout, stuck, or failed.

State and persistence: per-client state lives in `gsh_client->connection_manager` with mutex, condition variable, connection list, and count. Per-connection state lives in `xprt` custom data. Callback context is global under `callback_lock`. No durable persistence.

Dependencies and integration points: integrates with `client_mgr`, `xprt_handler`, `nfs_param.core_param.enable_connection_manager`, `connection_manager_metrics`, LTTng tracepoints, socket APIs, and ntirpc transport lifecycle (`SVC_DESTROY`, `svc_getrpccaller`).

Risks: correctness relies on lock ordering between client mutex and callback rwlock, plus careful unlock/relock around remote callbacks. Default callbacks refuse management, so startup ordering matters. Loopback connections are never managed. Forced linger can affect client-visible TCP behavior. The code reads `client` after `put_gsh_client()` in logging paths, which should be reviewed for lifetime safety depending on `gsh_client` retention.

Test signals: concurrent connection starts for the same client, remote drain success/failure, local drain with zero/active/stuck connections, drain cancellation by a new connection, non-managed loopback behavior, callback set/clear assertions, metrics emission, and transport-finish deregistration.
