# sources/user-network-fs/libtirpc/tirpc/rpc/svc.h

Purpose: `svc.h` defines the server-side RPC transport/request ABI, service registration APIs, dispatch helpers, event-loop entry points, and transport constructors.

Important APIs, types, and functions: Key items include service control constants, `enum xprt_stat`, `SVCXPRT`, `struct svc_req`, `svc_getrpccaller`, SVC operation macros, `svc_reg`, `svc_unreg`, `xprt_register`, `xprt_unregister`, reply/error helpers, `rpc_reg`, global fd/poll sets, `svc_getreq*`, `svc_run`, `svc_exit`, transport constructors `svc_create`, `svc_tp_create`, `svc_tli_create`, `svc_vc_create`, `svc_dg_create`, `svc_fd_create`, raw/unix compatibility constructors, cache enablement, and `__rpc_get_local_uid`.

Control flow: Servers create transports, register dispatch functions for program/version pairs, enter `svc_run` or call `svc_getreq*` from their own event loop, decode arguments via `SVC_GETARGS`, execute handlers, send replies/errors, free arguments, and eventually unregister/destroy transports.

State and persistence behavior: `SVCXPRT` persists fd/address/auth/private transport state. Global `svc_fdset`, `svc_pollfd`, and max fd/poll indices track registered transports. Service registration tables are implementation-owned. No durable service state is stored by the header itself.

Dependencies and integration points: It depends on XDR, auth, netconfig, rpc message types, and compatibility `svc_soc.h`. `svc_vc.c` implements the connection-oriented constructor declared here.

Risks: `SVCXPRT` layout is ABI-sensitive, including compatibility `xp_raddr` and private slots. Operation macros dereference vtables directly. Global fd sets need locking in multithreaded implementations. Batched TCP calls must avoid replies to prevent deadlocks.

Test signals: Tests should cover service registration/unregistration, dispatch of success and all standard errors, custom event-loop polling, transport create/destroy, version quiet controls, fd table updates, and batched-call no-reply behavior.
