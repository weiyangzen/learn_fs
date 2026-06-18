# sources/user-network-fs/nfs-utils/support/nfs/svc_create.c

Purpose: create and register RPC service listeners, using TI-RPC/netconfig when available and falling back to legacy `rpc_init()`.

Important APIs: `nfs_svc_create()` starts listeners for a program/version/dispatch function, and `nfs_svc_unregister()` removes rpcbind/portmap registrations. Internal TI-RPC helpers include `svc_create_bindaddr()`, `svc_create_sock()`, `svc_create_nconf_rand_port()`, `svc_create_nconf_fixed_port()`, and an 8-entry SVCXPRT cache.

Control flow: modern builds ignore SIGPIPE, set `RPC_SVC_CONNMAXREC_SET`, iterate visible netconfig entries, filter by global UDP/TCP protocol bits, choose either configured service port or caller-supplied port, then create/register transports. Random-port mode lets TI-RPC create xprts. Fixed-port mode pre-binds sockets with `SO_REUSEADDR`, IPv6-only when needed, nonblocking mode, and xprt caching so multiple versions can share the same listener. Legacy builds delegate to `rpc_init()`.

State and persistence: caches up to eight service transports in process memory. Registers service mappings with local rpcbind/portmapper. No file persistence.

Dependencies and integration: depends on libtirpc/netconfig, `rpcmisc.h` protocol globals, `svc_socket.c`, `sockaddr.h`, optional `tcpwrapper.h`, and `xlog`.

Risks: xprt cache has a fixed small size and logs only when full. `svc_reg()` may destroy xprts on failure, so cache consistency relies on only caching after successful registration. Fixed-port binding across IPv4/IPv6 depends on `IPV6_V6ONLY`. `rpc_control()` behavior is libtirpc-specific.

Test signals: random and fixed ports, multi-version same-port registration, UDP/TCP protocol filtering, IPv4/IPv6 listeners, cache-full behavior, `svc_reg()` failure, unregister, and legacy non-libtirpc build.
