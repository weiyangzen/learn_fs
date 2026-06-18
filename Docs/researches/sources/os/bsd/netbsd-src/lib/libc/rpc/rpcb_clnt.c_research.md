# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/rpcb_clnt.c

Read completely: 1271 lines.

Implements the client interface to rpcbind: `rpcb_set()`, `rpcb_unset()`, `rpcb_getaddr()`, `rpcb_getmaps()`, `rpcb_rmtcall()`, `rpcb_gettime()`, `rpcb_taddr2uaddr()`, `rpcb_uaddr2taddr()`, private `__rpcb_findaddr()`, and `__rpc_control()`.

The file maintains a small six-entry rpcbind address cache keyed by `(host, netid)`, protected by `rpcbaddr_cache_lock`. `getclnthandle()` checks the cache, deletes stale entries on failed client creation, resolves `sunrpc` with `getaddrinfo()`, creates an RPCB v4 client, and caches successful transport addresses plus optional universal address strings.

Local rpcbind access prefers the Unix-domain socket `_PATH_RPCBINDSOCK`; if that fails it discovers a loopback TCP transport from netconfig and connects to `127.0.0.1` or `::1`, caching the selected netconfig permanently.

`__rpcb_findaddr()` contains the main version-negotiation algorithm. With `PORTMAP`, IPv4 TCP/UDP first try portmapper v2. Then rpcbind v4/v3 are tried, using `RPCBPROC_GETADDRLIST` for connection-oriented transports via a datagram transport when possible, and falling back to `RPCBPROC_GETADDR`. It converts universal addresses to `netbuf`s and applies IPv6 scope fixup.

Registration sends owner as effective uid text. Remote calls use `RPCBPROC_CALLIT` across v4 then v3 and optionally return the responding address. Error paths set `rpc_createerr` with statuses such as `RPC_UNKNOWNPROTO`, `RPC_UNKNOWNHOST`, `RPC_PROGNOTREGISTERED`, `RPC_N2AXLATEFAILURE`, `RPC_PMAPFAILURE`, or `RPC_RPCBFAILURE`.
