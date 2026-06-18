# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_rpc_dispatcher_thread.c

## Purpose

This file initializes and wires NFS-Ganesha's libntirpc service side. It allocates UDP/TCP/VSOCK/RDMA sockets, binds them to configured ports, creates `SVCXPRT` transports, registers service programs with rpcbind when enabled, creates TI-RPC event channels, dispatches rendezvous callbacks for each protocol, allocates/free per-request objects, and manages per-transport NFS custom data.

Despite the filename, the current implementation is event-channel and transport setup code rather than a hand-written dispatcher thread loop. It is the front door for NFS, MOUNT, NLM, RQUOTA, NFSACL, VSOCK NFS, and NFS/RDMA depending on build and runtime options.

## Important APIs, types, and functions

Public startup/shutdown functions include `nfs_Init_netconfig`, `nfs_Init_svc`, `Create_SVCXPRTs`, `Bind_sockets`, `Clean_RPC`, `nfs_Get_netconfig`, and `nfs_get_evchannel_id`.

Global transport state includes `rpc_evchan[EVCHAN_SIZE]`, `pdata[P_COUNT]`, four `netconfig_*` pointers, `udp_socket[P_COUNT]`, `tcp_socket[P_COUNT]`, `udp_xprt[P_COUNT]`, `tcp_xprt[P_COUNT]`, and runtime flags `v6disabled`, `vsock`, and `rdma`.

Protocol gating is handled by `nfs_protocol_enabled`. RPC unregistration uses `unregister` and `unregister_rpc`. Socket lifecycle uses `Allocate_sockets`, `Allocate_sockets_V4`, `alloc_socket_setopts`, `enable_udp_listener`, optional `allocate_socket_vsock`, `Bind_sockets_V6`, `Bind_sockets_V4`, optional `bind_sockets_vsock`, and `close_rpc_fd`.

Transport creation uses `Create_udp`, `Create_tcp`, and optional `Create_RDMA`. UDP rendezvous callbacks are listed in `udp_dispatch`; TCP/RDMA callbacks are listed in `tcp_dispatch`. Each callback sets `xprt->xp_dispatch.process_cb` to the relevant validator (`nfs_rpc_valid_NFS`, `nfs_rpc_valid_MNT`, `nfs_rpc_valid_NLM`, `nfs_rpc_valid_RQUOTA`, `nfs_rpc_valid_NFSACL`, `nfs_rpc_valid_NFS_RDMA`) and returns the libntirpc status/receive result.

Per-transport data hooks are `nfs_rpc_alloc_user_data`, `nfs_rpc_free_user_data`, and `nfs_rpc_unref_user_data`. Per-request hooks supplied to `svc_init` are `alloc_nfs_request` and `free_nfs_request`.

Rpcbind registration is guarded by `RPCBIND` and uses `__Register_program`/`Register_program` plus `UDP_REGISTER` and `TCP_REGISTER` macros.

## Control flow

`nfs_Init_netconfig` must run before registration. It obtains `udp`, `tcp`, optional `udp6`, and optional `tcp6` entries from `/etc/netconfig`, logging fatal errors for missing IPv4 UDP/TCP and informational messages for missing IPv6 entries.

`nfs_Init_svc` configures `svc_init_params` from `nfs_param.core_param.rpc`: maximum connections, max events, send buffer, number of event channels, idle timeout, IOQ thread bounds, GSS context cache settings, optional pthread stack size, and optional RDMA limits. It calls `svc_init`, creates `EVCHAN_SIZE` event channels with `svc_rqst_new_evchan`, allocates sockets, binds them, unregisters stale rpcbind mappings, creates listening transports, and registers services with rpcbind when compiled in.

Socket allocation prefers IPv6 unless disabled by platform/runtime failure. For each enabled protocol, it optionally creates a UDP socket if `enable_udp_listener` permits it and always creates a TCP socket. `EAFNOSUPPORT` on IPv6 causes fallback to IPv4. `alloc_socket_setopts` applies `SO_REUSEADDR`, TCP keepalive options, UDP nonblocking mode, and optional `SO_BINDTODEVICE`.

Binding uses either IPv6 or IPv4 based on `v6disabled`, fills `proto_data` sockaddr/netbuf/t_bind structures, and binds each enabled protocol socket to `nfs_param.core_param.bind_addr` and `nfs_param.core_param.port[p]`. VSOCK binding is separate and nonfatal on failure.

Transport creation wraps sockets in libntirpc service transports. UDP uses `svc_dg_create` and registers with `UDP_UREG_CHAN`. TCP uses `svc_vc_ncreatef` with close/listen flags and registers with `TCP_UREG_CHAN`. RDMA uses `svc_rdma_create` with `rpc_rdma_xa`. All transports install `SVCSET_XP_FREE_USER_DATA`; TCP NFS connections additionally allocate NFS user data, install `SVCSET_XP_UNREF_USER_DATA`, initialize the connection manager, and set a `remote_addr_set_cb`.

Incoming request allocation is performed by libntirpc through `alloc_nfs_request`. It allocates `nfs_request_t`, references the transport, records XDR and transport pointers, initializes request reference count and duplicate-request queue linkage, increments health and metrics counters, and returns `&reqdata->svc`. `free_nfs_request` logs decode status, frees the request, releases the transport, increments dequeue counters, and records RPC completion metrics.

Shutdown through `Clean_RPC` unregisters programs, closes/destroys sockets and transports, and frees netconfig entries. The comment says it must be called only from the shutdown thread.

## State and persistence behavior

All state is process runtime state. Socket file descriptors and transport pointers are global arrays keyed by `protos`. Netconfig entries are cached globally until `Clean_RPC`. Event-channel IDs are cached in `rpc_evchan` and exposed by `nfs_get_evchannel_id`.

Per-transport custom data is attached to `SVCXPRT` internals through `init_custom_data_for_xprt`, duplicate request cache storage in `xp_u2`, connection-manager state, and later dissociation/destruction hooks. `nfs_rpc_free_user_data` releases any duplicate request cache with `nfs_dupreq_put_drc`, marks the connection finished, and destroys custom data.

Per-request state is allocated per decoded RPC request and persists until libntirpc calls the free hook. Health counters (`nfs_health_.enqueued_reqs`, `dequeued_reqs`) and monitoring counters track in-flight RPCs and completions.

RDMA configuration mutates the global `rpc_rdma_xa`, including assigning `port` with `strdup` and setting credits from config. There is no corresponding free in this file, so it is effectively process-lifetime state.

## Dependencies and integration points

This file depends heavily on libntirpc service APIs, rpcbind/netconfig APIs, POSIX sockets, protocol-specific NFS validators and dispatch functions, NFS core parameters, duplicate request cache code, transport custom-data helpers, connection manager hooks, LTTng tracepoints, and metrics.

Compile-time integration is broad: `_USE_NFS3`, `_USE_NLM`, `_USE_RQUOTA`, `USE_NFSACL3`, `RPC_VSOCK`, `_USE_NFS_RDMA`, `RPCBIND`, `__APPLE__`, and `__FreeBSD__` alter protocol lists, socket options, registration, and platform behavior.

Runtime integration is controlled by `NFS_options`, `nfs_param.core_param.enable_*` flags, UDP listener bitmasks, port arrays, bind address, RPC buffer sizes, TCP keepalive settings, max connection limits, and RDMA settings.

## Risks and edge cases

IPv4 binding code reuses members named `netbuf_udp6`, `bindaddr_udp6`, and `si_udp6` for IPv4 addresses. That is intentional storage reuse but confusing and error-prone; log messages in some IPv4 paths also mention `udp6`.

IPv6 fallback is global. Once one protocol observes `EAFNOSUPPORT`, `v6disabled` becomes true and later protocols allocate IPv4 sockets. Mixed IPv4/IPv6 behavior is not attempted.

`close_rpc_fd` closes raw sockets and then destroys transports, but `svc_vc_ncreatef` uses `SVC_CREATE_FLAG_CLOSE`; ownership assumptions must be correct to avoid double close. The existing order is longstanding but should be verified when changing libntirpc ownership flags.

`alloc_socket_setopts` applies `SO_BINDTODEVICE` only to TCP sockets, not UDP sockets. If interface binding is expected for UDP services too, this is a behavioral gap.

VSOCK bind failure is logged as major but startup continues. Deployments that requested VSOCK may need explicit health checks to notice that no VSOCK listener exists.

Rpcbind registration failure is fatal for v3-era services through `Register_program` but nonfatal for the optional v4 registration path using `__Register_program`. That matches NFSv4 rpcbind optionality but can surprise tests expecting uniform failure behavior.

Request health metrics depend on every allocated request reaching `free_nfs_request`. Decoder or transport paths that bypass the free hook would leave in-flight counts elevated.

## Test signals

Useful tests include netconfig lookup failures, IPv6 success and fallback to IPv4, UDP listener bitmask combinations, TCP keepalive option application, interface binding, socket bind failures, VSOCK requested/unavailable behavior, RDMA enabled/disabled behavior, rpcbind registration success/failure, and `Clean_RPC` resource cleanup.

Runtime integration tests should assert that each enabled protocol has the expected UDP/TCP transports, event channels are created and registered, `process_cb` is set to the correct validator after rendezvous, connection-manager hooks run on TCP NFS connections, duplicate request cache user data is freed, and request metrics balance enqueued/dequeued counts.
