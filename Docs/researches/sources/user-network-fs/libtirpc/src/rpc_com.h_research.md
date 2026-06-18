<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_com.h -->
# sources/user-network-fs/libtirpc/src/rpc_com.h

Purpose: private libtirpc common-interface header shared by client, server, rpcbind, and transport code. It wraps public `rpc/rpc_com.h` while declaring internal helpers that are not installed as public APIs.

Important APIs and types: declares `__rpc_set_netbuf`, `__rpcb_findaddr_timed`, `__rpc_control`, `__svc_clean_idle`, `__xdrrec_setnonblock`, `__xdrrec_getrec`, `__xprt_unregister_unlocked`, `__xprt_set_raddr`, and exported `__svc_maxrec`. It also defines fallback `SOL_IPV6`/`SOL_IP` aliases and `SUN_LEN_A()` for Linux abstract Unix sockets.

Control flow: no runtime logic except macro expansion. `SUN_LEN_A(ptr)` computes a `sockaddr_un` length for abstract Unix socket names by including the leading NUL path byte and the string that follows it.

State and persistence: declares, but does not define, shared service state (`__svc_maxrec`) and internal cross-module entry points.

Dependencies and integration points: included by `rpc_generic.c`, `rpcb_clnt.c`, `svc.c`, `svc_dg.c`, `rpcb_prot.c`, and other libtirpc internals. It connects address translation, rpcbind lookup, record-stream internals, and service transport registration.

Risks: this is a private ABI surface inside the library; signature drift here can break many source files. `SUN_LEN_A` assumes abstract-socket layout and uses `strlen(ptr->sun_path + 1)`, so callers must provide NUL-terminated abstract names.

Test signals: compile-time coverage across IPv4, IPv6, and Unix socket builds; runtime local rpcbind abstract-socket connection paths; record-stream nonblocking tests; and service unregister behavior using `__xprt_unregister_unlocked`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_com.h -->
