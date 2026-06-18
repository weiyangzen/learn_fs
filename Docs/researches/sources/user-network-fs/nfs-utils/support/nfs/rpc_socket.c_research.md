# sources/user-network-fs/nfs-utils/support/nfs/rpc_socket.c

Purpose: create RPC client handles over AF_LOCAL, UDP, or TCP sockets with bounded connect/request timeouts and optional privileged source ports.

Important APIs: `nfs_get_rpcclient()`, `nfs_get_priv_rpcclient()`, `nfs_getrpcbyname()`, and `nfs_authsys_create()`. Internal helpers cover local sockets, reserved-port binding, nonblocking connect, UDP client creation, and TCP client creation.

Control flow: public client creation validates address family and nonzero network port, clears `rpc_createerr`, then chooses TCP or UDP. UDP and TCP create sockets, optionally bind reserved ports, apply default timeout if `tv_sec == -1`, perform nonblocking connect with `select()`, and create TI-RPC or legacy RPC clients with `CLSET_FD_CLOSE`. UDP clients also set one-second retry timeout.

State and persistence: no durable state; mutates global `rpc_createerr`. `timeout` is an in/out parameter and may be reduced by `select()`.

Dependencies and integration: used by `getport.c` and other RPC callers. Depends on libtirpc when configured, `sockaddr.h`, `nfsrpc.h`, and AUTH_SYS APIs.

Risks: global `rpc_createerr` is not thread-local. `select()` timeout mutation can surprise callers reusing a timeval. Nonblocking connect restores original flags but errors during flag restore are ignored. Reserved ports require privileges and may fail under port exhaustion.

Test signals: TCP/UDP success, refused/timeouts, AF_LOCAL with libtirpc and legacy builds, reserved-port binding, IPv6 support, invalid protocol/address, and `nfs_authsys_create()` group-list minimization.
