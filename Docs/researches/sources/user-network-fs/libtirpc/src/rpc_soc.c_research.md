<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_soc.c -->
# sources/user-network-fs/libtirpc/src/rpc_soc.c

Purpose: legacy socket-style RPC compatibility layer compiled under `PORTMAP`. It maps old IPv4 TCP/UDP and Unix-domain APIs onto TIRPC client/server creation and rpcbind/portmap helpers.

Important APIs and functions: client helpers include `clntudp_bufcreate()`, `__libc_clntudp_bufcreate()`, `clntudp_create()`, `clnttcp_create()`, `clntraw_create()`, `clntunix_create()`, and AUTH_DES compatibility constructors. Server helpers include `svctcp_create()`, `svcudp_bufcreate()`, `svcudp_create()`, `svcfd_create()`, `svcraw_create()`, `svcunix_create()`, and `svcunixfd_create()`. Utility wrappers include `get_myaddress()`, `callrpc()`, `registerrpc()`, and `clnt_broadcast()`.

Control flow: `clnt_com_create()` obtains an IPv4 netconfig for tcp/udp, creates or uses a descriptor, optionally asks portmapper for a service port, binds a reserved port, and delegates to `clnt_tli_create`; ownership of auto-created descriptors is transferred to the client through `CLSET_FD_CLOSE`. `svc_com_create()` creates a descriptor if needed and delegates to `svc_tli_create`. Broadcast wraps modern `rpc_broadcast()` with a thread-specific legacy callback adapter. Unix-domain creation copies/binds/connects `sockaddr_un` addresses, including abstract socket support.

State and persistence: relies on external `rpcsoc_lock`, TSD key `clnt_broadcast_key`, and netconfig caches from `rpc_generic.c`. It mutates caller-provided socket variables and remote address port fields.

Dependencies and integration points: integrates old SunRPC APIs with `clnt_tli_create`, `svc_tli_create`, `rpc_call`, `rpc_reg`, `rpc_broadcast`, `pmap_getport`, and optional AUTH_DES support. IPv6 variants are present but disabled under `INET6_NOT_USED`.

Risks: most paths are IPv4-only despite TIRPC support. Some AUTH_DES constructors are stubs when `AUTHDES_SUPPORT` is absent. `svcunix_create()` ignores its incoming `sock` argument and creates a new descriptor. Legacy callback storage in thread-specific data means nested broadcasts need care.

Test signals: legacy UDP/TCP client creation with explicit and `RPC_ANYSOCK` descriptors, portmapper lookup fallback, descriptor close-on-destroy behavior, service creation and rpcbind/portmap registration, broadcast callback address conversion, Unix abstract and pathname socket clients/servers, and builds with and without `AUTHDES_SUPPORT`/`PORTMAP`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_soc.c -->
