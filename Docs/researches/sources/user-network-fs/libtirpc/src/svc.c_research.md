<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc.c -->
# sources/user-network-fs/libtirpc/src/svc.c

Purpose: core server-side RPC dispatch and transport registry. It tracks active transports, service program registrations, error replies, request authentication, and dispatch to application handlers.

Important APIs and functions: transport registry functions `xprt_register()`, `xprt_unregister()`, `__xprt_unregister_unlocked()`, and `svc_open_fds()` maintain `__svc_xports`, `svc_fdset`, and `svc_pollfd`. Service registration APIs `svc_reg()` and `svc_unreg()` manage rpcbind-backed callouts; `svc_register()`/`svc_unregister()` provide portmap compatibility under `PORTMAP`. Reply helpers include `svc_sendreply()`, `svcerr_noproc()`, `svcerr_decode()`, `svcerr_systemerr()`, `svcerr_auth()`, `svcerr_weakauth()`, `svcerr_noprog()`, and `svcerr_progvers()`. Input paths are `svc_getreq()`, `svc_getreqset()`, `svc_getreq_common()`, and `svc_getreq_poll()`. `rpc_control()` gets/sets `__svc_maxrec`.

Control flow: registration inserts `SVCXPRT` pointers by fd into `__svc_xports`, updates `fd_set` state for select, and appends/reuses poll slots for poll-based loops. `svc_reg()` determines a netid from transport/netconfig/fd, stores a callout keyed by program/version/netid, optionally registers with local rpcbind, and stores the netid on the transport. `svc_getreq_common()` receives one or more batched requests from a transport, authenticates with `_gss_authenticate`, skips dispatch for GSS handshake/control requests when requested, finds matching program/version callouts, invokes the dispatch routine, or emits program/version errors.

State and persistence: process-global `__svc_xports`, `svc_head`, `svc_fdset`, `svc_pollfd`, `svc_maxfd`, `svc_max_pollfd`, and `__svc_maxrec`. Registry state is protected by `svc_fd_lock` and `svc_lock`. Per-request credentials are stack-backed in `cred_area`.

Dependencies and integration points: uses transport ops through `SVC_RECV`, `SVC_REPLY`, `SVC_STAT`, and `SVC_DESTROY`; authentication from `svc_auth.c`; rpcbind/portmap registration; and common data from `rpc_commondata.c`.

Risks: callout traversal in `svc_getreq_common()` is not visibly under `svc_lock`, so concurrent registration/unregistration must be considered carefully. `svc_unreg()` frees `sc_netid` with an incorrect size expression, though `mem_free` may ignore the size. Descriptor values >= `_rpc_dtablesize()` are not registered in `__svc_xports`.

Test signals: registering multiple transports and netids for one program/version, duplicate dispatch rejection, rpcbind registration/unregistration, dispatch success, missing procedure/program/version replies, GSS no-dispatch handshakes, transport death during recursive dispatch, poll `POLLNVAL` cleanup, and `rpc_control` validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc.c -->
