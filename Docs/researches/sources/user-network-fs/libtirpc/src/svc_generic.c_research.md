<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_generic.c -->
# sources/user-network-fs/libtirpc/src/svc_generic.c

Purpose: high-level service creation over arbitrary netconfig/nettype transports. It opens/binds/listens descriptors and delegates to stream or datagram transport implementations.

Important APIs and functions: `svc_create()` creates or reuses transports across all netconfigs selected by a nettype. `svc_tp_create()` creates one transport for one `netconfig` and registers a program/version. `svc_tli_create()` is the generic descriptor/netconfig transport constructor.

Control flow: `svc_create()` iterates selected netconfigs, reuses existing transports by `xp_netid` from a static list, unregisters stale mappings, registers the new program/version, or creates a new transport via `svc_tp_create()` and stores it in the reuse list. `svc_tli_create()` opens a socket when fd is `RPC_ANYFD`, or derives socket info from the supplied fd; binds to a dynamic port when unbound and no bind address is supplied; otherwise binds to requested address and listens; then chooses `svc_fd_create` for accepted stream sockets, `svc_vc_create` for listening stream sockets, or `svc_dg_create` for datagram sockets.

State and persistence: `svc_create()` keeps a static process-global list of created transports protected by `xprtlist_lock`. Created transports persist until application destruction or process exit. `svc_tli_create()` fills `xp_type`, `xp_netid`, and `xp_tp`.

Dependencies and integration points: depends on `__rpc_setconf`/`__rpc_getconf`, `__rpc_nconf2fd`, `__rpc_fd2sockinfo`, `__rpc_sockisbound`, `__binddynport`, `svc_vc_create`, `svc_fd_create`, `svc_dg_create`, and rpcbind registration via `svc_reg`.

Risks: the static transport reuse list has no removal path, so destroyed transports can leave stale pointers if applications destroy them independently. `listen()` is called even for dynamically bound sockets before final transport-type switch. Error paths must carefully avoid closing caller-owned descriptors.

Test signals: create services over `netpath`, `tcp`, `udp`, and visible nettypes; reuse a transport for multiple program versions; accepted stream fd detection; dynamic bind success/failure; caller-owned fd cleanup behavior; rpcbind unregister/register ordering; and service destruction after failed registration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_generic.c -->
