# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_soc.c

Read completely: 430 lines.

Provides old socket-based RPC compatibility APIs when compiled with `PORTMAP`. Client constructors `clntudp_bufcreate()`, `clntudp_create()`, and `clnttcp_create()` are built on a shared `clnt_com_create()` that resolves tcp/udp netconfig, optionally creates a socket, looks up a port with `pmap_getport()`, binds a reserved local port, and calls `clnt_tli_create()`.

Server constructors `svctcp_create()`, `svcudp_bufcreate()`, `svcudp_create()`, `svcfd_create()`, and `svcraw_create()` adapt old interfaces to `svc_tli_create()`, `svc_fd_create()`, and `svc_raw_create()`. `get_myaddress()` returns loopback `PMAPPORT`. `callrpc()` and `registerrpc()` forward to `rpc_call()` and `rpc_reg()`.

`clnt_broadcast()` adapts the old sockaddr-in callback signature to `rpc_broadcast()` using thread-specific or global callback storage. The whole file is compatibility glue for TCP/UDP-only pre-netconfig RPC.
