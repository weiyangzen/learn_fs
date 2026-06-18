# sources/user-network-fs/libtirpc/tirpc/rpc/svc_soc.h

Purpose: `svc_soc.h` exposes legacy socket-specific server APIs for backward compatibility with pre-TI-RPC code.

Important APIs, types, and functions: It defines `svc_getcaller`, `svc_getcaller_netbuf`, and declares `svc_register`, `svc_unregister`, `svcraw_create`, UDP constructors/cache APIs, optional IPv6 UDP constructors, TCP constructors, and `svcfd_create`.

Control flow: Legacy callers create UDP/TCP/fd/raw transports, register program/version dispatchers with an IP protocol number, and access caller addresses through old sockaddr-compatible macros.

State and persistence behavior: The header owns no state. Implementations create `SVCXPRT` objects and use the same global service registration and fd tables as modern APIs.

Dependencies and integration points: It is included from `svc.h` and maps old socket APIs onto modern `svc_vc_create`, `svc_dg_create`, `svc_fd_create`, and raw transports.

Risks: `svc_getcaller` exposes legacy `xp_raddr`, while newer code should use `xp_rtaddr`; keeping both coherent is required. IPv6 declarations depend on build configuration. Old `u_long` program/version types must remain compatible with `rpcprog_t`/`rpcvers_t`.

Test signals: Compatibility tests should build and run old `svctcp_create`, `svcudp_create`, `svc_register`, and `svc_getcaller` users, including IPv6 variants when enabled.
