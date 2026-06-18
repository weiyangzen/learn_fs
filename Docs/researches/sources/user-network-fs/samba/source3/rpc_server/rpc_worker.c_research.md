# sources/user-network-fs/samba/source3/rpc_server/rpc_worker.c

## Purpose
`rpc_worker.c` is the generic runtime used by every `rpcd_*` helper. It implements two modes: `--list-interfaces`, which prints worker limits and served endpoint bindings for `samba-dcerpcd`, and worker mode, which registers endpoint servers, receives client sockets from the host, and runs DCE/RPC packet processing.

## Important APIs, Types, And Functions
`struct rpc_worker` stores active ncacn connections, host pid, messaging context, dcesrv context, callbacks, status counters, completion state, and connection timestamps. Public `rpc_worker_main` is the entry point used by concrete daemons. Interface listing uses `rpc_worker_print_interface`. Host status is sent through `rpc_worker_report_status`. Client handoff is processed by `rpc_worker_new_client_filter` and `rpc_worker_new_client`. Connection teardown uses `rpc_worker_connection_terminated` and `dcesrv_connection_destructor`. Worker-local association group IDs are managed by `rpc_worker_assoc_group_new`, `rpc_worker_assoc_group_reference`, and `rpc_worker_assoc_group_find`. The async shell is `rpc_worker_send`, `rpc_worker_done`, `rpc_worker_shutdown`, and `rpc_worker_recv`.

## Control Flow
`rpc_worker_main` parses common options. In list mode it reads optional loadparm overrides for `num_workers` and `idle_seconds`, prints them, then prints each NDR interface syntax and endpoint list. In worker mode it initializes logging, smbd shim callbacks, signals, guest/system sessions, messaging, dcesrv context callbacks, and endpoint server implementations returned by the concrete daemon. It then registers each endpoint server and enters a tevent loop. New-client messages carry one fd plus an NDR-encoded `rpc_host_client`. The worker parses the binding, resolves the endpoint, rebuilds remote and local tsocket addresses from named-pipe auth data, wraps the socket in an NPA or BSD tstream, enforces that system tokens are only accepted over NCALRPC, connects to the endpoint, parses the already-read bind packet, adds the connection to the active list, updates counters, and calls `dcesrv_loop_next_packet`.

## State And Persistence
State is per-process and in-memory: active connection list, association group IDR through the global dcesrv context, connection counters, status messages, and timestamps. No durable files are written by this generic layer except logs and core/debug outputs configured by Samba. Association group IDs encode worker index in the high 16 bits and a worker-local random ID in the low 16 bits, matching host routing logic.

## Dependencies And Integration Points
It depends on command-line helpers, Samba messaging, tevent, talloc, dcesrv core, generated `ndr_rpc_host`, named-pipe auth, smbd shims, winbind toggling, source3 auth, security tokens, endpoint server registration, and concrete daemon callbacks for interfaces and endpoint servers. It is tightly coupled to `rpc_host.c` message types `MSG_RPC_HOST_NEW_CLIENT`, `MSG_RPC_WORKER_STATUS`, `MSG_RPC_WORKER_INFO`, `MSG_RPC_DUMP_STATUS`, and `MSG_SHUTDOWN`.

## Risks And Test Signals
Risks include fd/message ownership, accepting malformed serialized clients, mismatched endpoint strings after dynamic port assignment, transport/auth mismatches, system-token restrictions, association group leaks or counter drift, and duplicate assignment to `state->new_client_req` for different filtered reads. Test signals are helper `--list-interfaces` output, host-to-worker socket fd transfer, TCP and named-pipe binds, associated binds routed to the correct worker index, invalid worker indexes, `MSG_RPC_WORKER_INFO` and dump-status output, SIGHUP config reload, shutdown behavior, and counter updates after connection termination.
